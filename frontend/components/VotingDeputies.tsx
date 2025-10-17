import { useQuery } from 'react-query'
import api from '@/lib/api'
import { UserGroupIcon } from '@heroicons/react/24/outline'

interface Deputy {
  party: string
  first_name: string
  last_name: string
  vote: 'ZA' | 'PRZECIW' | 'WSTRZYMAŁ' | 'NIE GŁOSOWAŁ' | 'OBECNY'
}

interface VotingDeputiesProps {
  billId: number
}

export default function VotingDeputies({ billId }: VotingDeputiesProps) {
  const { data, isLoading, error } = useQuery(
    ['voting-pdf-data', billId],
    async () => {
      const response = await api.get(`/bills/${billId}/pdf-data/`)
      return response.data
    },
    {
      enabled: !!billId,
      retry: false,
      refetchOnWindowFocus: false
    }
  )

  const getVoteColor = (vote: string) => {
    switch (vote.toUpperCase()) {
      case 'ZA':
        return 'text-green-600 bg-green-100 dark:bg-green-900 dark:text-green-200'
      case 'PRZECIW':
        return 'text-red-600 bg-red-100 dark:bg-red-900 dark:text-red-200'
      case 'WSTRZYMAŁ':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900 dark:text-yellow-200'
      case 'NIE GŁOSOWAŁ':
        return 'text-gray-600 bg-gray-100 dark:bg-gray-700 dark:text-gray-200'
      case 'OBECNY':
        return 'text-blue-600 bg-blue-100 dark:bg-blue-900 dark:text-blue-200'
      default:
        return 'text-gray-600 bg-gray-100 dark:bg-gray-700 dark:text-gray-200'
    }
  }

  const getVoteText = (vote: string) => {
    switch (vote.toUpperCase()) {
      case 'ZA':
        return 'Za'
      case 'PRZECIW':
        return 'Przeciw'
      case 'WSTRZYMAŁ':
        return 'Wstrzymał'
      case 'NIE GŁOSOWAŁ':
        return 'Nie głosował'
      case 'OBECNY':
        return 'Obecny'
      default:
        return vote
    }
  }

  if (isLoading) {
    return (
      <div className="mt-4">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-4"></div>
          <div className="space-y-2">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (error || !data || !data.deputies || data.deputies.length === 0) {
    return (
      <div className="mt-4 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
        <div className="flex items-center">
          <UserGroupIcon className="h-5 w-5 text-yellow-600 mr-2" />
          <span className="text-sm text-yellow-800 dark:text-yellow-200">
            Nie udało się odczytać danych posłów z PDF-a
          </span>
        </div>
      </div>
    )
  }

  // Grupuj posłów według partii
  const deputiesByParty = data.deputies.reduce((acc: { [key: string]: Deputy[] }, deputy: Deputy) => {
    if (!acc[deputy.party]) {
      acc[deputy.party] = []
    }
    acc[deputy.party].push(deputy)
    return acc
  }, {})

  // Nie sortujemy - wyświetlamy dokładnie tak jak w pliku PDF
  const sortedDeputiesByParty = deputiesByParty

  return (
    <div className="mt-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Głosy posłów ({data.total_count})
        </h3>
      </div>
      
      <div className="space-y-6">
        {Object.entries(sortedDeputiesByParty).map(([party, deputies]) => (
          <div key={party} className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
            <div className="bg-gray-50 dark:bg-gray-800 px-4 py-3 border-b border-gray-200 dark:border-gray-700">
              <h4 className="font-semibold text-gray-900 dark:text-white">{party}</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {deputies.length} posłów
              </p>
            </div>
            <div className="max-h-64 overflow-y-auto">
              <div className="divide-y divide-gray-200 dark:divide-gray-700">
                {deputies.map((deputy, index) => (
                  <div key={index} className="px-4 py-3 flex items-center justify-between">
                    <div className="flex-1">
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {deputy.first_name} {deputy.last_name}
                      </span>
                    </div>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getVoteColor(deputy.vote)}`}>
                      {getVoteText(deputy.vote)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
