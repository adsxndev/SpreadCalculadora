document.addEventListener('DOMContentLoaded', function() {
    // Elementos do DOM
    const spotAberturaInput = document.getElementById('spotAbertura');
    const shortAberturaInput = document.getElementById('shortAbertura');
    const spotFechamentoInput = document.getElementById('spotFechamento');
    const shortFechamentoInput = document.getElementById('shortFechamento');
    const spreadAberturaElement = document.getElementById('spreadAbertura');
    const spreadFechamentoElement = document.getElementById('spreadFechamento');
    const lucroElement = document.getElementById('lucro');
    const saveButton = document.getElementById('saveButton');
    const errorMessageElement = document.getElementById('errorMessage');
    const deleteModal = document.getElementById('deleteModal');
    const cancelDeleteBtn = document.getElementById('cancelDelete');
    const confirmDeleteBtn = document.getElementById('confirmDelete');
    
    // Função para obter o token CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');
    
    // Variável para armazenar o ID do registro a ser excluído
    let deleteId = null;
    
    // Função para calcular o spread
    function calcularSpread(spot, short, invertido = false) {
        if (!spot || !short) return null;
        
        const spotValue = parseFloat(spot);
        const shortValue = parseFloat(short);
        
        if (isNaN(spotValue) || isNaN(shortValue) || spotValue <= 0) return null;
        
        const spread = ((shortValue - spotValue) / spotValue * 100);
        return parseFloat((invertido ? -spread : spread).toFixed(2));
    }
    
    // Função para atualizar os resultados
    function atualizarResultados() {
        // Calcular spread de abertura (normal)
        const spreadAbertura = calcularSpread(spotAberturaInput.value, shortAberturaInput.value, false);
        if (spreadAbertura !== null) {
            spreadAberturaElement.textContent = spreadAbertura + '%';
        } else {
            spreadAberturaElement.textContent = '—';
        }
        
        // Calcular spread de fechamento (invertido)
        const spreadFechamento = calcularSpread(spotFechamentoInput.value, shortFechamentoInput.value, true);
        if (spreadFechamento !== null) {
            spreadFechamentoElement.textContent = spreadFechamento + '%';
        } else {
            spreadFechamentoElement.textContent = '—';
        }
        
        // Calcular lucro
        if (spreadAbertura !== null && spreadFechamento !== null) {
            // Usando o valor absoluto do spread de fechamento para evitar dupla negação
            const lucro = parseFloat((spreadAbertura + spreadFechamento).toFixed(2));
            lucroElement.textContent = lucro + '%';
            
            if (lucro > 0) {
                lucroElement.classList.add('profit');
                lucroElement.classList.remove('loss');
            } else if (lucro < 0) {
                lucroElement.classList.add('loss');
                lucroElement.classList.remove('profit');
            } else {
                lucroElement.classList.remove('profit', 'loss');
            }
        } else {
            lucroElement.textContent = '—';
            lucroElement.classList.remove('profit', 'loss');
        }
    }
    
    // Função para mostrar o modal de confirmação
    function showDeleteModal(id) {
        deleteId = id;
        deleteModal.classList.add('active');
    }
    
    // Função para esconder o modal de confirmação
    function hideDeleteModal() {
        deleteModal.classList.remove('active');
        deleteId = null;
    }
    
    // Função para salvar no histórico
    async function salvarNoHistorico() {
        try {
            if (!spotAberturaInput.value || !shortAberturaInput.value || 
                !spotFechamentoInput.value || !shortFechamentoInput.value) {
                errorMessageElement.textContent = 'Preencha todos os campos antes de salvar';
                return;
            }
            
            const spreadAbertura = calcularSpread(spotAberturaInput.value, shortAberturaInput.value, false);
            const spreadFechamento = calcularSpread(spotFechamentoInput.value, shortFechamentoInput.value, true);
            
            if (spreadAbertura === null || spreadFechamento === null) {
                errorMessageElement.textContent = 'Erro ao calcular os valores';
                return;
            }
            
            const data = {
                spot_abertura: spotAberturaInput.value,
                short_abertura: shortAberturaInput.value,
                spot_fechamento: spotFechamentoInput.value,
                short_fechamento: shortFechamentoInput.value,
                spread_abertura: spreadAbertura,
                spread_fechamento: spreadFechamento,
                lucro: parseFloat((spreadAbertura + spreadFechamento).toFixed(2))
            };
            
            const response = await fetch('/api/salvar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Erro ao salvar operação');
            }
            
            // Limpar campos após salvar com sucesso
            spotAberturaInput.value = '';
            shortAberturaInput.value = '';
            spotFechamentoInput.value = '';
            shortFechamentoInput.value = '';
            
            // Atualizar resultados
            atualizarResultados();
            
            // Recarregar a página para mostrar a nova operação
            window.location.reload();
            
        } catch (err) {
            console.error('Erro:', err);
            errorMessageElement.textContent = err.message || 'Erro ao salvar operação';
        }
    }
    
    // Função para excluir uma operação
    async function excluirOperacao() {
        if (!deleteId) return;
        
        try {
            const response = await fetch(`/api/excluir/${deleteId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': csrftoken
                }
            });
            
            if (!response.ok) {
                const result = await response.json();
                throw new Error(result.error || 'Erro ao excluir operação');
            }
            
            // Recarregar a página para atualizar a lista
            window.location.reload();
            
        } catch (err) {
            console.error('Erro:', err);
            errorMessageElement.textContent = err.message || 'Erro ao excluir operação';
            hideDeleteModal();
        }
    }
    
    // Event listeners para inputs
    spotAberturaInput.addEventListener('input', atualizarResultados);
    shortAberturaInput.addEventListener('input', atualizarResultados);
    spotFechamentoInput.addEventListener('input', atualizarResultados);
    shortFechamentoInput.addEventListener('input', atualizarResultados);
    
    // Event listener para o botão de salvar
    saveButton.addEventListener('click', salvarNoHistorico);
    
    // Event listeners para o modal
    cancelDeleteBtn.addEventListener('click', hideDeleteModal);
    confirmDeleteBtn.addEventListener('click', excluirOperacao);
    
    // Event listeners para os botões de exclusão
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            showDeleteModal(id);
        });
    });
    
    // Inicializar resultados
    atualizarResultados();
});