import { useQuery } from 'react-query'
import api from '@/lib/api'
import Link from 'next/link'
import { format } from 'date-fns'
import { pl } from 'date-fns/locale'

interface Bill {
  id: number
  title: string
  description: string
  number: string
  status: string
  authors: string
  submission_date: string
  support_votes: number
  against_votes: number
  neutral_votes: number
  total_votes: number
  support_percentage: number
  is_featured: boolean
  created_at: string
}

export default function FeaturedBills() {
  const { data: bills, isLoading } = useQuery<Bill[]>(
    'featured-bills',
    async () => {
      const response = await api.get('/bills/featured/')
      return response.data
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
          Wyróżnione projekty ustaw
        </h2>
        <Link
          href="/bills"
          className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 font-medium"
        >
          Zobacz wszystkie →
        </Link>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {bills?.map((bill) => (
          <div key={bill.id} className="card p-6 hover:shadow-md transition-shadow duration-200">
            <div className="flex items-start justify-between mb-3">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(bill.status)}`}>
                {getStatusText(bill.status)}
              </span>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {bill.number}
              </span>
            </div>
            
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2">
              {bill.title}
            </h3>
            
            <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-3">
              {bill.description}
            </p>
            
            <div className="mb-4">
              <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
                <span>Poparcie</span>
                <span>{bill.support_percentage}%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${bill.support_percentage}%` }}
                ></div>
              </div>
            </div>
            
            <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 mb-4">
              <span>{bill.total_votes} głosów</span>
              <span>{format(new Date(bill.submission_date), 'dd MMM yyyy', { locale: pl })}</span>
            </div>
            
            <Link
              href={`/bills/${bill.id}`}
              className="btn-outline w-full text-center"
            >
              Zobacz szczegóły
            </Link>
          </div>
        ))}
      </div>
      
      {bills?.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400">
            Brak wyróżnionych projektów ustaw
          </p>
        </div>
      )}
    </div>
  )
}

