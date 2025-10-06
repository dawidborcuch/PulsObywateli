import { useQuery } from 'react-query'
import api from '@/lib/api'
import Link from 'next/link'
import { format } from 'date-fns'
import { pl } from 'date-fns/locale'
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'

interface Poll {
  id: number
  title: string
  description: string
  poll_type: string
  options: string[]
  start_date: string
  end_date: string
  total_votes: number
  is_ongoing: boolean
  is_expired: boolean
  results: { [key: string]: { votes: number; percentage: number } }
  is_featured: boolean
  created_at: string
}

export default function FeaturedPolls() {
  const { data: polls, isLoading } = useQuery<Poll[]>(
    'featured-polls',
    async () => {
      const response = await api.get('/polls/featured/')
      return response.data
    }
  )

  const getPollTypeColor = (type: string) => {
    const typeColors: { [key: string]: string } = {
      'political': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      'social': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      'economic': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      'other': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
    }
    return typeColors[type] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
  }

  const getPollTypeText = (type: string) => {
    const typeTexts: { [key: string]: string } = {
      'political': 'Polityczny',
      'social': 'Społeczny',
      'economic': 'Ekonomiczny',
      'other': 'Inny',
    }
    return typeTexts[type] || type
  }

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4']

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="card p-6 animate-pulse">
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-4 w-3/4"></div>
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Wyróżnione sondaże
        </h2>
        <Link
          href="/polls"
          className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 font-medium"
        >
          Zobacz wszystkie →
        </Link>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {polls?.map((poll) => {
          const chartData = poll.options.map((option, index) => ({
            name: option,
            value: poll.results[option]?.votes || 0,
            color: COLORS[index % COLORS.length]
          }))

          return (
            <div key={poll.id} className="card p-6 hover:shadow-md transition-shadow duration-200">
              <div className="flex items-start justify-between mb-3">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPollTypeColor(poll.poll_type)}`}>
                  {getPollTypeText(poll.poll_type)}
                </span>
                <span className={`text-xs font-medium ${
                  poll.is_ongoing 
                    ? 'text-green-600 dark:text-green-400' 
                    : poll.is_expired 
                    ? 'text-red-600 dark:text-red-400'
                    : 'text-yellow-600 dark:text-yellow-400'
                }`}>
                  {poll.is_ongoing ? 'Aktywny' : poll.is_expired ? 'Zakończony' : 'Nadchodzący'}
                </span>
              </div>
              
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2">
                {poll.title}
              </h3>
              
              <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-3">
                {poll.description}
              </p>
              
              {poll.total_votes > 0 && (
                <div className="mb-4">
                  <div className="h-32">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={chartData}
                          cx="50%"
                          cy="50%"
                          innerRadius={20}
                          outerRadius={40}
                          dataKey="value"
                        >
                          {chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  
                  <div className="mt-2 space-y-1">
                    {poll.options.slice(0, 3).map((option, index) => (
                      <div key={option} className="flex items-center justify-between text-xs">
                        <div className="flex items-center">
                          <div 
                            className="w-3 h-3 rounded-full mr-2"
                            style={{ backgroundColor: COLORS[index % COLORS.length] }}
                          ></div>
                          <span className="text-gray-600 dark:text-gray-400 truncate">
                            {option}
                          </span>
                        </div>
                        <span className="text-gray-900 dark:text-white font-medium">
                          {poll.results[option]?.percentage || 0}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 mb-4">
                <span>{poll.total_votes} głosów</span>
                <span>
                  {format(new Date(poll.end_date), 'dd MMM yyyy', { locale: pl })}
                </span>
              </div>
              
              <Link
                href={`/polls/${poll.id}`}
                className="btn-outline w-full text-center"
              >
                {poll.is_ongoing ? 'Głosuj' : 'Zobacz wyniki'}
              </Link>
            </div>
          )
        })}
      </div>
      
      {polls?.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400">
            Brak wyróżnionych sondaży
          </p>
        </div>
      )}
    </div>
  )
}

