
<template>
  <div class="container">
    <h1>Busca de Operadoras de Saúde</h1>
    
    <div class="search-container">
      <input
        v-model="searchTerm"
        @input="handleSearch"
        placeholder="Digite nome, CNPJ ou registro..."
        class="search-input"
      />
      <button @click="search" class="search-button">Buscar</button>
    </div>

    <div v-if="loading" class="loading">Carregando...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="results.length > 0" class="results-container">
      <div v-for="(item, index) in results" :key="index" class="result-card">
        <h3>{{ item.dados.razao_social || 'N/A' }}</h3>
        <p v-if="item.dados.nome_fantasia">
          <strong>Nome Fantasia:</strong> {{ item.dados.nome_fantasia }}
        </p>
        <p><strong>Registro ANS:</strong> {{ item.dados.registro_ans || 'N/A' }}</p>
        <p><strong>CNPJ:</strong> {{ formatCNPJ(item.dados.cnpj) }}</p>
        <p><strong>Relevância:</strong> {{ item.relevancia }}%</p>
        <p><strong>Modalidade:</strong> {{ item.dados.modalidade || 'N/A' }}</p>
        <p><strong>Localização:</strong> {{ item.dados.cidade }}/{{ item.dados.uf }}</p>
        
        <button @click="showDetails(item.dados.registro_ans)" class="details-button">
          Ver Detalhes
        </button>
      </div>
    </div>

    <div v-else-if="searchTerm && !loading" class="no-results">
      Nenhum resultado encontrado para "{{ searchTerm }}"
    </div>

    <!-- Modal de Detalhes -->
    <div v-if="selectedOperator" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <span class="close-button" @click="closeModal">&times;</span>
        <h2>{{ selectedOperator.razao_social }}</h2>
        
        <div class="modal-grid">
          <div>
            <h3>Informações Básicas</h3>
            <p><strong>Nome Fantasia:</strong> {{ selectedOperator.nome_fantasia || 'N/A' }}</p>
            <p><strong>CNPJ:</strong> {{ formatCNPJ(selectedOperator.cnpj) }}</p>
            <p><strong>Registro ANS:</strong> {{ selectedOperator.registro_ans }}</p>
          </div>
          
          <div>
            <h3>Endereço</h3>
            <p><strong>Logradouro:</strong> {{ selectedOperator.logradouro || 'N/A' }}</p>
            <p><strong>Número:</strong> {{ selectedOperator.numero || 'N/A' }}</p>
            <p><strong>Bairro:</strong> {{ selectedOperator.bairro || 'N/A' }}</p>
            <p><strong>Cidade/UF:</strong> {{ selectedOperator.cidade }}/{{ selectedOperator.uf }}</p>
          </div>
          
          <div>
            <h3>Contato</h3>
            <p><strong>Telefone:</strong> {{ formatPhone(selectedOperator.telefone) }}</p>
            <p v-if="selectedOperator.fax"><strong>Fax:</strong> {{ selectedOperator.fax }}</p>
            <p v-if="selectedOperator.endereco_eletronico">
              <strong>Email:</strong> {{ selectedOperator.endereco_eletronico }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      searchTerm: '',
      results: [],
      loading: false,
      error: null,
      searchTimeout: null,
      selectedOperator: null
    };
  },
  methods: {
    async search() {
      if (!this.searchTerm.trim()) {
        this.results = [];
        return;
      }

      this.loading = true;
      this.error = null;

      try {
        const response = await axios.get('http://localhost:5000/api/buscar', {
          params: { q: this.searchTerm }
        });
        
        console.log('Dados recebidos:', response.data);
        this.results = response.data;
        
        if (this.results.length === 0) {
          this.error = 'Nenhum resultado encontrado. Tente termos diferentes.';
        }
      } catch (err) {
        console.error('Erro na busca:', err);
        this.error = err.response?.data?.error || 'Erro ao conectar com o servidor';
        this.results = [];
      } finally {
        this.loading = false;
      }
    },
    
    async showDetails(registroAns) {
      try {
        this.loading = true;
        const response = await axios.get(`http://localhost:5000/api/detalhes/${registroAns}`);
        this.selectedOperator = response.data;
      } catch (err) {
        console.error('Erro ao buscar detalhes:', err);
        this.error = 'Erro ao carregar detalhes da operadora';
      } finally {
        this.loading = false;
      }
    },
    
    closeModal() {
      this.selectedOperator = null;
    },
    
    handleSearch() {
      clearTimeout(this.searchTimeout);
      this.searchTimeout = setTimeout(() => {
        this.search();
      }, 500);
    },
    
    formatCNPJ(cnpj) {
      if (!cnpj || cnpj === 'N/A') return 'N/A';
      
      const cleaned = cnpj.toString().replace(/\D/g, '');
      
      if (cleaned.length === 14) {
        return cleaned.replace(
          /^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/,
          '$1.$2.$3/$4-$5'
        );
      }
      return cnpj;
    },
    
    formatPhone(phone) {
      if (!phone) return 'N/A';
      
      const cleaned = phone.toString().replace(/\D/g, '');
      
      if (cleaned.length === 10) {
        return cleaned.replace(
          /^(\d{2})(\d{4})(\d{4})$/,
          '($1) $2-$3'
        );
      }
      if (cleaned.length === 11) {
        return cleaned.replace(
          /^(\d{2})(\d{5})(\d{4})$/,
          '($1) $2-$3'
        );
      }
      return phone;
    }
  }
};
</script>

<style>
/* Estilos gerais */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Arial', sans-serif;
  
}

h1 {
  color: #2c3e50;
  text-align: center;
  margin-bottom: 2rem;
}

/* Barra de busca */
.search-container {
  display: flex;
  gap: 10px;
  margin-bottom: 2rem;
}

.search-input {
  flex: 1;
  padding: 10px 15px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.search-button {
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.search-button:hover {
  background-color: #369f6b;
}

/* Resultados */
.results-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.result-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.result-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.result-card h3 {
  margin-top: 0;
  color: #2c3e50;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.details-button {
  margin-top: 15px;
  padding: 8px 16px;
  background-color: #369f6b;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.details-button:hover {
  background-color: #13633b;
}

/* Mensagens */
.loading, .no-results, .error {
  text-align: center;
  padding: 20px;
  font-size: 18px;
}

.loading {
  color: #666;
}

.no-results {
  color: #888;
  font-style: italic;
}

.error {
  color: #e74c3c;
  font-weight: bold;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
}

.close-button {
  position: absolute;
  top: 15px;
  right: 15px;
  font-size: 24px;
  cursor: pointer;
  color: #777;
}

.close-button:hover {
  color: #333;
}

.modal-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

/* Responsividade */
@media (max-width: 768px) {
  .search-container {
    flex-direction: column;
  }
  
  .results-container {
    grid-template-columns: 1fr;
  }
  
  .modal-grid {
    grid-template-columns: 1fr;
  }
}
</style>