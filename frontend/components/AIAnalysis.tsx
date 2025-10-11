import { useQuery } from 'react-query'
import api from '@/lib/api'
import { 
  SparklesIcon, 
  ExclamationTriangleIcon, 
  CheckCircleIcon, 
  ClockIcon
} from '@heroicons/react/24/outline'

interface AIAnalysis {
  changes: string
  risks: string
  benefits: string
  error?: string
}

interface AIAnalysisResponse {
  analysis: AIAnalysis
  analysis_date: string
  bill_id: number
  bill_title: string
}

interface AIAnalysisProps {
  billId: number
  billTitle: string
}

export default function AIAnalysis({ billId, billTitle }: AIAnalysisProps) {
  // Pobierz analizę AI
  const { data: analysisData, isLoading, error } = useQuery<AIAnalysisResponse>(
    ['ai-analysis', billId],
    async () => {
      const response = await api.get(`/bills/${billId}/ai-analysis/`)
      return response.data
    },
    {
      enabled: !!billId,
      retry: false,
      refetchOnWindowFocus: false
    }
  )

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pl-PL', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (isLoading) {
    return (
      <div className="card p-6">
        <div className="flex items-center space-x-2 mb-4">
          <SparklesIcon className="h-5 w-5 text-primary-600" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Analiza AI
          </h2>
        </div>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card p-6">
        <div className="flex items-center space-x-2 mb-4">
          <SparklesIcon className="h-5 w-5 text-primary-600" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Analiza AI
          </h2>
        </div>
        
        <div className="text-center py-8">
          <SparklesIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Analiza AI niedostępna
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Analiza AI dla tego projektu nie została jeszcze wygenerowana lub wystąpił błąd podczas jej pobierania.
          </p>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            <p>Analiza AI jest automatycznie generowana dla nowych projektów ustaw.</p>
            <p>Jeśli projekt jest nowy, analiza może być jeszcze w trakcie generowania.</p>
          </div>
        </div>
      </div>
    )
  }

  if (!analysisData) {
    return null
  }

  const { analysis, analysis_date } = analysisData

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <SparklesIcon className="h-5 w-5 text-primary-600" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Analiza AI
          </h2>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
          <ClockIcon className="h-4 w-4" />
          <span>Wygenerowano: {formatDate(analysis_date)}</span>
        </div>
      </div>

      <div className="space-y-6">
        {/* Najważniejsze zmiany */}
        {analysis.changes && (
          <div className="border-l-4 border-blue-500 pl-4">
            <div className="flex items-center space-x-2 mb-3">
              <CheckCircleIcon className="h-5 w-5 text-blue-600" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Najważniejsze zmiany
              </h3>
            </div>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              {analysis.changes}
            </p>
          </div>
        )}

        {/* Zagrożenia */}
        {analysis.risks && (
          <div className="border-l-4 border-red-500 pl-4">
            <div className="flex items-center space-x-2 mb-3">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Zagrożenia dla Państwa Polskiego
              </h3>
            </div>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              {analysis.risks}
            </p>
          </div>
        )}

        {/* Korzyści */}
        {analysis.benefits && (
          <div className="border-l-4 border-green-500 pl-4">
            <div className="flex items-center space-x-2 mb-3">
              <CheckCircleIcon className="h-5 w-5 text-green-600" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Korzyści dla Państwa Polskiego
              </h3>
            </div>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              {analysis.benefits}
            </p>
          </div>
        )}

        {/* Błąd analizy */}
        {analysis.error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />
              <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                Błąd analizy
              </h3>
            </div>
            <p className="text-sm text-red-700 dark:text-red-300">
              {analysis.error}
            </p>
          </div>
        )}
      </div>

    </div>
  )
}
