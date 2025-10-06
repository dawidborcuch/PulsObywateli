import { useQuery } from 'react-query'
import api from '@/lib/api'
import Link from 'next/link'
import { 
  DocumentTextIcon, 
  ChartBarIcon, 
  UsersIcon, 
  ChatBubbleLeftRightIcon 
} from '@heroicons/react/24/outline'

interface StatsData {
  total_bills: number
  active_bills: number
  total_votes: number
  most_supported_bill: {
    id: number
    title: string
    support_percentage: number
  } | null
  most_controversial_bill: {
    id: number
    title: string
    against_votes: number
  } | null
  status_distribution: { [key: string]: number }
  recent_bills: Array<{
    id: number
    title: string
    number: string
    support_percentage: number
  }>
}

export default function Stats() {
  const { data: stats, isLoading } = useQuery<StatsData>(
    'stats',
    async () => {
      const response = await api.get('/bills/stats/')
      return response.data
    }
  )

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="text-center animate-pulse">
                <div className="h-12 w-12 bg-gray-200 dark:bg-gray-700 rounded-lg mx-auto mb-4"></div>
                <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mx-auto"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  const statItems = [
    {
      name: 'Projekty ustaw',
      value: stats?.total_bills || 0,
      icon: DocumentTextIcon,
      color: 'text-blue-600 dark:text-blue-400',
      bgColor: 'bg-blue-100 dark:bg-blue-900',
    },
    {
      name: 'Aktywne projekty',
      value: stats?.active_bills || 0,
      icon: ChartBarIcon,
      color: 'text-green-600 dark:text-green-400',
      bgColor: 'bg-green-100 dark:bg-green-900',
    },
    {
      name: 'Oddane głosy',
      value: stats?.total_votes || 0,
      icon: UsersIcon,
      color: 'text-purple-600 dark:text-purple-400',
      bgColor: 'bg-purple-100 dark:bg-purple-900',
    },
    {
      name: 'Komentarze',
      value: '1,234', // Placeholder - would need comments stats endpoint
      icon: ChatBubbleLeftRightIcon,
      color: 'text-orange-600 dark:text-orange-400',
      bgColor: 'bg-orange-100 dark:bg-orange-900',
    },
  ]

  return (
    <div className="bg-white dark:bg-gray-800 py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Statystyki platformy
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Sprawdź jak rozwija się nasza społeczność
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {statItems.map((item) => (
            <div key={item.name} className="text-center">
              <div className={`inline-flex items-center justify-center w-12 h-12 rounded-lg ${item.bgColor} mb-4`}>
                <item.icon className={`w-6 h-6 ${item.color}`} />
              </div>
              <div className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                {typeof item.value === 'number' ? item.value.toLocaleString() : item.value}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {item.name}
              </div>
            </div>
          ))}
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {stats?.most_supported_bill && (
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Najbardziej popierany projekt
              </h3>
              <div className="space-y-3">
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white line-clamp-2">
                    {stats.most_supported_bill.title}
                  </h4>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      Poparcie
                    </span>
                    <span className="text-lg font-semibold text-green-600 dark:text-green-400">
                      {stats.most_supported_bill.support_percentage}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${stats.most_supported_bill.support_percentage}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {stats?.most_controversial_bill && (
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Najbardziej kontrowersyjny projekt
              </h3>
              <div className="space-y-3">
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white line-clamp-2">
                    {stats.most_controversial_bill.title}
                  </h4>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      Głosy przeciw
                    </span>
                    <span className="text-lg font-semibold text-red-600 dark:text-red-400">
                      {stats.most_controversial_bill.against_votes}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        
        <div className="text-center mt-12">
          <Link
            href="/bills"
            className="btn-primary"
          >
            Przeglądaj wszystkie projekty
          </Link>
        </div>
      </div>
    </div>
  )
}

