import Head from 'next/head'
import Layout from '@/components/Layout'
import { useQuery } from 'react-query'
import api from '@/lib/api'
import { format } from 'date-fns'
import { pl } from 'date-fns/locale'
import { TrophyIcon, ChartBarIcon, UsersIcon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline'

interface Bill {
  id: number
  title: string
  number: string
  support_percentage: number
  total_votes: number
  status: string
}

interface Poll {
  id: number
  title: string
  total_votes: number
  poll_type: string
}

export default function RankingPage() {
  const { data: bills, isLoading: billsLoading } = useQuery<Bill[]>(
    'top-bills',
    async () => {
      const response = await api.get('/bills/?ordering=-support_votes&limit=10')
      return response.data.results || response.data
    }
  )

  const { data: polls, isLoading: pollsLoading } = useQuery<Poll[]>(
    'top-polls',
    async () => {
      const response = await api.get('/polls/?ordering=-total_votes&limit=10')
      return response.data.results || response.data
    }
  )

  const { data: stats } = useQuery(
    'ranking-stats',
    async () => {
      const [billsStats, pollsStats] = await Promise.all([
        api.get('/bills/stats/'),
        api.get('/polls/stats/')
      ])
      return {
        bills: billsStats.data,
        polls: pollsStats.data
      }
    }
  )

  const getStatusColor = (status: string) => {
    const statusColors: { [key: string]: string } = {
      'draft': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
      'submitted': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      'in_committee': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      'first_reading': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      'second_reading': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
      'third_reading': 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200',
      'passed': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      'rejected': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      'withdrawn': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
    }
    return statusColors[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
  }

  const getStatusText = (status: string) => {
    const statusTexts: { [key: string]: string } = {
      'draft': 'Projekt',
      'submitted': 'Złożony',
      'in_committee': 'W komisji',
      'first_reading': 'Pierwsze czytanie',
      'second_reading': 'Drugie czytanie',
      'third_reading': 'Trzecie czytanie',
      'passed': 'Przyjęty',
      'rejected': 'Odrzucony',
      'withdrawn': 'Wycofany',
    }
    return statusTexts[status] || status
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

  return (
    <>
      <Head>
        <title>Ranking - PulsObywateli</title>
        <meta name="description" content="Ranking najpopularniejszych projektów ustaw i sondaży" />
      </Head>
      
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              Ranking
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400">
              Najpopularniejsze projekty ustaw i sondaże
            </p>
          </div>

          {/* Statystyki */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
              <div className="card p-6 text-center">
                <TrophyIcon className="h-8 w-8 text-yellow-500 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats.bills.total_bills}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Projekty ustaw
                </div>
              </div>
              
              <div className="card p-6 text-center">
                <ChartBarIcon className="h-8 w-8 text-blue-500 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats.polls.total_polls}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Sondaże
                </div>
              </div>
              
              <div className="card p-6 text-center">
                <UsersIcon className="h-8 w-8 text-green-500 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats.bills.total_votes + stats.polls.total_votes}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Łączne głosy
                </div>
              </div>
              
              <div className="card p-6 text-center">
                <ChatBubbleLeftRightIcon className="h-8 w-8 text-purple-500 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats.bills.total_votes}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Głosy na ustawy
                </div>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Top projekty ustaw */}
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
                🏆 Najpopularniejsze projekty ustaw
              </h2>
              
              {billsLoading ? (
                <div className="space-y-4">
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="animate-pulse">
                      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
                      <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="space-y-4">
                  {bills?.map((bill, index) => (
                    <div key={bill.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="flex-shrink-0 w-8 h-8 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
                          <span className="text-sm font-bold text-primary-600 dark:text-primary-400">
                            {index + 1}
                          </span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                            {bill.title}
                          </h3>
                          <div className="flex items-center space-x-2 mt-1">
                            <span className="text-xs text-gray-500 dark:text-gray-400">
                              {bill.number}
                            </span>
                            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(bill.status)}`}>
                              {getStatusText(bill.status)}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-semibold text-gray-900 dark:text-white">
                          {bill.support_percentage}%
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          {bill.total_votes} głosów
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Top sondaże */}
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
                📊 Najpopularniejsze sondaże
              </h2>
              
              {pollsLoading ? (
                <div className="space-y-4">
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="animate-pulse">
                      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
                      <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="space-y-4">
                  {polls?.map((poll, index) => (
                    <div key={poll.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="flex-shrink-0 w-8 h-8 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
                          <span className="text-sm font-bold text-primary-600 dark:text-primary-400">
                            {index + 1}
                          </span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                            {poll.title}
                          </h3>
                          <div className="flex items-center space-x-2 mt-1">
                            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                              poll.poll_type === 'political' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                              poll.poll_type === 'social' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                              poll.poll_type === 'economic' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                              'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                            }`}>
                              {getPollTypeText(poll.poll_type)}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-semibold text-gray-900 dark:text-white">
                          {poll.total_votes}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          głosów
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </Layout>
    </>
  )
}
