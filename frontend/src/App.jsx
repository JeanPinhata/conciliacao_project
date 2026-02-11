import { useState } from 'react'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('pagamento')
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')
  const API_URL = 'http://localhost:8000'

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.pdf')) {
        setError('Por favor, selecione um arquivo PDF válido.')
        return
      }
      setFile(selectedFile)
      setError('')
      setSuccess(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      setError('Por favor, selecione um arquivo PDF.')
      return
    }

    setLoading(true)
    setError('')
    setSuccess(false)

    try {
      const formData = new FormData()
      formData.append('file', file)
      
      let tipo = 'PAGAMENTO'
      if (activeTab === 'recebimento') tipo = 'RECEBIMENTO'
      if (activeTab === 'extrato') tipo = 'EXTRATO'
      formData.append('tipo', tipo)

      const response = await fetch(`${API_URL}/processar`, {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        },
      })

      if (!response.ok) {
        throw new Error('Erro ao processar o arquivo.')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `conciliacao_${activeTab}.xlsx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      setSuccess(true)
      setFile(null)
      const input = document.querySelector('input[type="file"]')
      if (input) input.value = ''
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <div className="container">
        <h1>Conciliador Bancário Inteligente</h1>
        <p>Processe seus extratos bancários automaticamente</p>
        <div className="card">
          <div className="tabs">
            <button
              className={`tab ${activeTab === 'pagamento' ? 'active' : ''}`}
              onClick={() => setActiveTab('pagamento')}
            >
              Pagamentos
            </button>
            <button
              className={`tab ${activeTab === 'recebimento' ? 'active' : ''}`}
              onClick={() => setActiveTab('recebimento')}
            >
              Recebimentos
            </button>
            <button
              className={`tab ${activeTab === 'extrato' ? 'active' : ''}`}
              onClick={() => setActiveTab('extrato')}
            >
              Extratos
            </button>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="upload-area">
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                id="file-input"
              />
              <label htmlFor="file-input">
                📄 Clique para selecionar ou arraste um arquivo PDF
              </label>
              {file && <p className="file-name">✓ {file.name}</p>}
            </div>
            <button type="submit" disabled={!file || loading} className="submit-btn">
              {loading ? 'Processando...' : 'Processar e Baixar'}
            </button>
          </form>
          {success && <div className="alert success">✓ Arquivo processado com sucesso!</div>}
          {error && <div className="alert error">✗ {error}</div>}
        </div>
      </div>
    </div>
  )
}

export default App