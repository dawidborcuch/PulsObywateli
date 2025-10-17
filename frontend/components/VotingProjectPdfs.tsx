import { useQuery } from 'react-query'
import api from '@/lib/api'
import { DocumentIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline'

interface ProjectPdf {
  name: string
  url: string
  type: 'main_attachment' | 'additional_print'
}

interface VotingProjectPdfsData {
  project_pdfs: ProjectPdf[]
  print_numbers: string[]
  total_count: number
}

interface VotingProjectPdfsProps {
  billId: number
}

export default function VotingProjectPdfs({ billId }: VotingProjectPdfsProps) {
  const { data, isLoading, error } = useQuery<VotingProjectPdfsData>(
    ['votingProjectPdfs', billId],
    async () => {
      const response = await api.get(`/bills/${billId}/project-pdfs/`)
      return response.data
    },
    {
      enabled: !!billId,
      retry: false,
      refetchOnWindowFocus: false
    }
  )

  if (isLoading) {
    return (
      <div className="card p-6">
        <div className="flex items-center space-x-2 mb-4">
          <DocumentIcon className="h-5 w-5 text-primary-600" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            PDF-y projektów ustaw
          </h2>
        </div>
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
        </div>
      </div>
    )
  }

  if (error || !data || data.project_pdfs.length === 0) {
    return (
      <div className="card p-6">
        <div className="flex items-center space-x-2 mb-4">
          <DocumentIcon className="h-5 w-5 text-primary-600" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            PDF-y projektów ustaw
          </h2>
        </div>
        <div className="text-center py-8">
          <DocumentIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Brak PDF-ów projektów
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            {data?.message || 'Dla tego głosowania nie ma dostępnych PDF-ów projektów ustaw.'}
          </p>
        </div>
      </div>
    )
  }

  const mainPdfs = data.project_pdfs.filter(pdf => pdf.type === 'main_attachment')
  const additionalPdfs = data.project_pdfs.filter(pdf => pdf.type === 'additional_print')

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center">
          <DocumentIcon className="h-6 w-6 text-primary-500 mr-2" />
          PDF-y projektów ustaw
        </h2>
        <div className="text-sm text-gray-500 dark:text-gray-400">
          {data.total_count} plików
        </div>
      </div>

      <div className="space-y-6">
        {/* Numery druków */}
        {data.print_numbers.length > 0 && (
          <div className="mb-4">
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Numery druków: {data.print_numbers.join(', ')}
            </h3>
          </div>
        )}

        {/* Główne załączniki */}
        {mainPdfs.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Główne dokumenty
            </h3>
            <div className="space-y-3">
              {mainPdfs.map((pdf, index) => (
                <div key={index} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-gray-50 dark:bg-gray-800">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <DocumentIcon className="h-8 w-8 text-red-600" />
                      <div>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {pdf.name}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          Główny dokument
                        </p>
                      </div>
                    </div>
                    <a
                      href={pdf.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                    >
                      <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
                      Pobierz PDF
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Dodatkowe druki */}
        {additionalPdfs.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Dodatkowe druki
            </h3>
            <div className="space-y-3">
              {additionalPdfs.map((pdf, index) => (
                <div key={index} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-gray-50 dark:bg-gray-800">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <DocumentIcon className="h-8 w-8 text-blue-600" />
                      <div>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {pdf.name}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          Dodatkowy druk
                        </p>
                      </div>
                    </div>
                    <a
                      href={pdf.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
                      Pobierz PDF
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
