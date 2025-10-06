import { useState } from 'react'
import Head from 'next/head'
import Layout from '@/components/Layout'
import { useQuery } from 'react-query'
import api from '@/lib/api'
import { format } from 'date-fns'
import { pl } from 'date-fns/locale'
import { MagnifyingGlassIcon, FunnelIcon } from '@heroicons/react/24/outline'
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

export default function PollsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const { data: polls, isLoading, error } = useQuery<Poll[]>(
    ['polls', searchTerm, typeFilter, statusFilter],
    async () => {
      try {
        const params = new URLSearchParams()
        if (searchTerm) params.append('search', searchTerm)
        if (typeFilter) params.append('poll_type', typeFilter)
        if (statusFilter) params.append('status', statusFilter)
        
        const response = await api.get(`/polls/?${params.toString()}`)
        console.log('Polls API Response:', response.data) // Debug log
        return response.data.results || response.data || []
      } catch (error) {
        console.error('Polls API Error:', error)
        throw error
      }
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

  if (error) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-red-600 dark:text-red-400 mb-4">
              Błąd ładowania sondaży
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Spróbuj odświeżyć stronę lub skontaktuj się z administratorem.
            </p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <>
      <Head>
        <title>Sondaże - PulsObywateli</title>
        <meta name="description" content="Głosuj w sondażach społecznych i politycznych" />
      </Head>
      
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              Sondaże
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400">
              Głosuj w sondażach społecznych i politycznych
            </p>
          </div>

          {/* Filtry i wyszukiwanie */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Szukaj sondaży..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                />
              </div>
              
              <div className="relative">
                <FunnelIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                >
                  <option value="">Wszystkie typy</option>
                  <option value="political">Polityczny</option>
                  <option value="social">Społeczny</option>
                  <option value="economic">Ekonomiczny</option>
                  <option value="other">Inny</option>
                </select>
              </div>
              
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              >
                <option value="">Wszystkie statusy</option>
                <option value="ongoing">Aktywne</option>
                <option value="upcoming">Nadchodzące</option>
                <option value="expired">Zakończone</option>
              </select>
            </div>
          </div>

          {/* Lista sondaży */}
          {isLoading ? (
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
          ) : (
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
                    
                    <button className="btn-outline w-full text-center">
                      {poll.is_ongoing ? 'Głosuj' : 'Zobacz wyniki'}
                    </button>
                  </div>
                )
              })}
            </div>
          )}
          
          {polls?.length === 0 && !isLoading && (
            <div className="text-center py-12">
              <p className="text-gray-500 dark:text-gray-400">
                Brak sondaży spełniających kryteria wyszukiwania
              </p>
            </div>
          )}
        </div>
      </Layout>
    </>
  )
}
