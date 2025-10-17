import { useState } from 'react'
import Head from 'next/head'
import Link from 'next/link'
import Layout from '@/components/Layout'
import { useQuery } from 'react-query'
import api from '@/lib/api'
import { format } from 'date-fns'
import { pl } from 'date-fns/locale'
import { MagnifyingGlassIcon, FunnelIcon, ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline'

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
  project_type: string
  data_source: string
  sejm_id: string
  eli: string
  passed: boolean
  // Nowe pola z API Sejmu
  voting_date?: string
  voting_number?: string
  session_number?: string
  voting_topic?: string
  voting_results?: {
    total_voted: number
    za: number
    przeciw: number
    wstrzymali: number
    nie_glosowalo: number
    majority_votes: number
    majority_type: string
  }
}

export default function BillsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [sortBy, setSortBy] = useState('-session_number,-voting_number')
  const [currentPage, setCurrentPage] = useState(1)

  const { data: billsData, isLoading, error } = useQuery(
    ['bills', searchTerm, statusFilter, sortBy, currentPage],
    async () => {
      try {
        const params = new URLSearchParams()
        if (searchTerm) params.append('search', searchTerm)
        if (statusFilter) params.append('status', statusFilter)
        if (sortBy) params.append('ordering', sortBy)
        params.append('page', currentPage.toString())
        
        const response = await api.get(`/bills/?${params.toString()}`)
        console.log('API Response:', response.data) // Debug log
        return response.data
      } catch (error) {
        console.error('API Error:', error)
        throw error
      }
    }
  )

  const bills = billsData?.results || billsData || []
  const pagination = billsData?.pagination || null

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
      'I czytanie': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      'II czytanie': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
      'III czytanie': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      'Senat': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
      'Sprawozdanie': 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-200',
      'Nominacja': 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200',
      'Opinia': 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
      'W trakcie': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
      'Wpłynął do Sejmu': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      'Skierowano do I czytania': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
      'Praca w komisjach': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      'Uchwalono': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
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
      'I czytanie': 'I czytanie',
      'II czytanie': 'II czytanie',
      'III czytanie': 'III czytanie',
      'Senat': 'Senat',
      'Sprawozdanie': 'Sprawozdanie',
      'Nominacja': 'Nominacja',
      'Opinia': 'Opinia',
      'W trakcie': 'W trakcie',
      'Wpłynął do Sejmu': 'Wpłynął do Sejmu',
      'Skierowano do I czytania': 'Skierowano do I czytania',
      'Praca w komisjach': 'Praca w komisjach',
      'Uchwalono': 'Uchwalono',
    }
    return statusTexts[status] || status
  }

  if (error) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-red-600 dark:text-red-400 mb-4">
              Błąd ładowania projektów ustaw
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
        <title>Projekty ustaw - PulsObywateli</title>
        <meta name="description" content="Przeglądaj i głosuj na projekty ustaw w Polsce" />
      </Head>
      
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              Projekty ustaw
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400">
              Przeglądaj i głosuj na projekty ustaw w Polsce
            </p>
          </div>

          {/* Filtry i wyszukiwanie */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Szukaj projektów..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                />
              </div>
              
              <div className="relative">
                <FunnelIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                >
                  <option value="">Wszystkie statusy</option>
                  <option value="Wpłynął do Sejmu">Wpłynął do Sejmu</option>
                  <option value="Skierowano do I czytania">Skierowano do I czytania</option>
                  <option value="I czytanie">I czytanie</option>
                  <option value="Praca w komisjach">Praca w komisjach</option>
                  <option value="II czytanie">II czytanie</option>
                  <option value="III czytanie">III czytanie</option>
                  <option value="Senat">Senat</option>
                  <option value="Uchwalono">Uchwalono</option>
                  <option value="Sprawozdanie">Sprawozdanie</option>
                  <option value="Nominacja">Nominacja</option>
                  <option value="Opinia">Opinia</option>
                  <option value="W trakcie">W trakcie</option>
                </select>
              </div>
              
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              >
                <option value="-session_number,-voting_number">Najnowsze głosowania</option>
                <option value="session_number,voting_number">Najstarsze głosowania</option>
                <option value="-submission_date">Najnowsze projekty</option>
                <option value="submission_date">Najstarsze projekty</option>
                <option value="-total_votes">Najpopularniejsze</option>
                <option value="-support_votes">Najbardziej popierane</option>
              </select>
            </div>
          </div>

          {/* Lista projektów */}
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
              {bills?.map((bill) => (
                <div key={bill.id} className="card p-6 hover:shadow-md transition-shadow duration-200">
                  {/* Informacja o posiedzeniu */}
                  {bill.session_number && (
                    <div className="mb-3">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                        Posiedzenie Sejmu nr {bill.session_number}
                      </span>
                    </div>
                  )}
                  
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2">
                    {bill.title}
                  </h3>
                  
                  <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-3">
                    {bill.description}
                  </p>
                  
                  {/* Wyniki głosowania */}
                  {bill.voting_results && (
                    <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
                        {bill.description?.includes('kworum') ? 'Wyniki kworum' : 'Wyniki głosowania'}
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        {bill.description?.includes('kworum') ? (
                          <>
                            <div className="flex items-center justify-between">
                              <span className="text-blue-600 dark:text-blue-400">Obecni:</span>
                              <span className="font-medium text-blue-600 dark:text-blue-400">{bill.voting_results.total_voted - bill.voting_results.nie_glosowalo}</span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-gray-600 dark:text-gray-400">Nie głosowało:</span>
                              <span className="font-medium text-gray-600 dark:text-gray-400">{bill.voting_results.nie_glosowalo}</span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-gray-500 dark:text-gray-500">Łącznie:</span>
                              <span className="font-medium text-gray-500 dark:text-gray-500">{bill.voting_results.total_voted}</span>
                            </div>
                          </>
                        ) : (
                          <>
                            <div className="flex items-center justify-between">
                              <span className="text-green-600 dark:text-green-400">Za:</span>
                              <span className="font-medium text-green-600 dark:text-green-400">{bill.voting_results.za}</span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-red-600 dark:text-red-400">Przeciw:</span>
                              <span className="font-medium text-red-600 dark:text-red-400">{bill.voting_results.przeciw}</span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-yellow-600 dark:text-yellow-400">Wstrzymali:</span>
                              <span className="font-medium text-yellow-600 dark:text-yellow-400">{bill.voting_results.wstrzymali}</span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-gray-600 dark:text-gray-400">Nie głosowało:</span>
                              <span className="font-medium text-gray-600 dark:text-gray-400">{bill.voting_results.nie_glosowalo}</span>
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                  )}
                  
                  <div className="flex items-center justify-end text-sm text-gray-500 dark:text-gray-400 mb-4">
                    {bill.voting_date ? (
                      <div className="text-right">
                        <div className="font-medium">Głosowanie nr {bill.voting_number}</div>
                        <div className="text-xs">
                          {format(new Date(bill.voting_date), 'dd MMM yyyy HH:mm', { locale: pl })}
                        </div>
                      </div>
                    ) : (
                      <span>{format(new Date(bill.submission_date), 'dd MMM yyyy', { locale: pl })}</span>
                    )}
                  </div>
                  
                  <Link href={`/bills/${bill.id}`}>
                    <button className="btn-outline w-full text-center">
                      Zobacz szczegóły
                    </button>
                  </Link>
                </div>
              ))}
            </div>
          )}
          
          {bills?.length === 0 && !isLoading && (
            <div className="text-center py-12">
              <p className="text-gray-500 dark:text-gray-400">
                Brak projektów ustaw spełniających kryteria wyszukiwania
              </p>
            </div>
          )}

          {/* Paginacja */}
          {pagination && pagination.count > pagination.page_size && (
            <div className="mt-8 flex items-center justify-between">
              <div className="text-sm text-gray-700 dark:text-gray-300">
                Wyświetlane {((currentPage - 1) * pagination.page_size) + 1}-{Math.min(currentPage * pagination.page_size, pagination.count)} z {pagination.count} projektów
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setCurrentPage(currentPage - 1)}
                  disabled={!pagination.previous}
                  className="flex items-center px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-800 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
                >
                  <ChevronLeftIcon className="w-4 h-4 mr-1" />
                  Poprzednia
                </button>
                
                <div className="flex items-center space-x-1">
                  {Array.from({ length: Math.min(5, pagination.num_pages) }, (_, i) => {
                    const pageNum = Math.max(1, currentPage - 2) + i
                    if (pageNum > pagination.num_pages) return null
                    
                    return (
                      <button
                        key={pageNum}
                        onClick={() => setCurrentPage(pageNum)}
                        className={`px-3 py-2 text-sm font-medium rounded-md ${
                          pageNum === currentPage
                            ? 'bg-primary-600 text-white'
                            : 'text-gray-500 bg-white border border-gray-300 hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700'
                        }`}
                      >
                        {pageNum}
                      </button>
                    )
                  })}
                </div>
                
                <button
                  onClick={() => setCurrentPage(currentPage + 1)}
                  disabled={!pagination.next}
                  className="flex items-center px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-800 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
                >
                  Następna
                  <ChevronRightIcon className="w-4 h-4 ml-1" />
                </button>
              </div>
            </div>
          )}
        </div>
      </Layout>
    </>
  )
}

// Funkcje pomocnicze dla wyświetlania typu projektu
function getProjectTypeText(projectType: string): string {
  const typeMap: { [key: string]: string } = {
    'rządowy': 'Projekt Rządowy',
    'obywatelski': 'Projekt Obywatelski',
    'poselski': 'Projekt Poselski',
    'senacki': 'Projekt Senacki',
    'prezydencki': 'Projekt Prezydencki',
    'unknown': 'Projekt Nieznany'
  }
  return typeMap[projectType] || 'Projekt Nieznany'
}

function getProjectTypeColor(projectType: string): string {
  const colorMap: { [key: string]: string } = {
    'rządowy': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'obywatelski': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'poselski': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    'senacki': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    'prezydencki': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    'unknown': 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
  }
  return colorMap[projectType] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
}

// Funkcje pomocnicze dla paska postępu legislacyjnego
function getLegislativeProgress(status: string): number {
  const progressMap: { [key: string]: number } = {
    'Wpłynął do Sejmu': 10,
    'Skierowano do I czytania': 20,
    'I czytanie': 30,
    'Praca w komisjach': 40,
    'II czytanie': 60,
    'III czytanie': 80,
    'Senat': 90,
    'Uchwalono': 100,
    'Sprawozdanie': 25,
    'Nominacja': 15,
    'Opinia': 20,
    'W trakcie': 50,
  }
  return progressMap[status] || 0
}

function getLegislativeProgressColor(status: string): string {
  const colorMap: { [key: string]: string } = {
    'Wpłynął do Sejmu': 'bg-blue-500',
    'Skierowano do I czytania': 'bg-indigo-500',
    'I czytanie': 'bg-purple-500',
    'Praca w komisjach': 'bg-yellow-500',
    'II czytanie': 'bg-orange-500',
    'III czytanie': 'bg-pink-500',
    'Senat': 'bg-red-500',
    'Uchwalono': 'bg-green-500',
    'Sprawozdanie': 'bg-cyan-500',
    'Nominacja': 'bg-emerald-500',
    'Opinia': 'bg-amber-500',
    'W trakcie': 'bg-gray-500',
  }
  return colorMap[status] || 'bg-gray-500'
}

function getStageActiveClass(currentStatus: string, stageStatus: string): string {
  const stageOrder = ['Wpłynął do Sejmu', 'I czytanie', 'II czytanie', 'III czytanie', 'Senat', 'Uchwalono']
  const currentIndex = stageOrder.indexOf(currentStatus)
  const stageIndex = stageOrder.indexOf(stageStatus)
  
  if (currentIndex >= stageIndex) {
    return 'text-primary-600 dark:text-primary-400 font-medium'
  }
  return 'text-gray-400 dark:text-gray-500'
}
