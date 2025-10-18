import { useState } from 'react'
import Head from 'next/head'
import Link from 'next/link'
import Layout from '@/components/Layout'
import { useQuery } from 'react-query'
import api from '@/lib/api'
import { format } from 'date-fns'
import { pl } from 'date-fns/locale'
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline'

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
  const [sortBy, setSortBy] = useState('-session_number,-voting_number')
  const [currentPage, setCurrentPage] = useState(1)

  const { data: billsData, isLoading, error } = useQuery(
    ['bills', sortBy, currentPage],
    async () => {
      try {
        const params = new URLSearchParams()
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
              Głosowania w sejmie
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400">
              Demokracja działa, gdy głos obywateli jest słyszany — zobacz, jak głosowali posłowie i powiedz, co o tym myślisz.
            </p>
          </div>

          {/* Sortowanie */}
          <div className="flex items-center justify-end mb-6">
            <div className="flex items-center space-x-3">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Sortuj:
              </span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              >
                <option value="-session_number,-voting_number">Najnowsze głosowania</option>
                <option value="session_number,voting_number">Najstarsze głosowania</option>
                <option value="-voting_date">Najnowsza data głosowania</option>
                <option value="voting_date">Najstarsza data głosowania</option>
                <option value="-created_at">Najnowsze dodane</option>
                <option value="created_at">Najstarsze dodane</option>
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
                <div key={bill.id} className="card p-6 hover:shadow-md transition-shadow duration-200 flex flex-col justify-between min-h-[500px]">
                  <div className="flex-1">
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
                  
                  {/* Najważniejsze zmiany wg. AI - tylko dla głosowań z analizą AI */}
                  {bill.ai_analysis && 
                   !bill.description?.toLowerCase().includes('kworum') && 
                   !bill.description?.toLowerCase().includes('wniosek o odroczenie posiedzenia') && (
                    <div className="mb-4 p-3 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 border border-purple-200 dark:border-purple-800 rounded-lg">
                      <div className="flex items-center mb-2">
                        <div className="w-6 h-6 bg-purple-100 dark:bg-purple-800 rounded-full flex items-center justify-center mr-2">
                          <span className="text-purple-600 dark:text-purple-400 text-xs font-semibold">AI</span>
                        </div>
                        <h4 className="text-sm font-semibold text-purple-900 dark:text-purple-100">
                          Najważniejsze zmiany wg. AI
                        </h4>
                      </div>
                      <p className="text-xs text-purple-800 dark:text-purple-200 leading-relaxed">
                        {bill.ai_analysis.changes}
                      </p>
                    </div>
                  )}
                  
                  {/* Definicja dla głosowań kworum */}
                  {bill.description?.toLowerCase().includes('kworum') && (
                    <div className="mb-4 p-3 bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                      <div className="flex items-center mb-2">
                        <div className="w-6 h-6 bg-blue-100 dark:bg-blue-800 rounded-full flex items-center justify-center mr-2">
                          <span className="text-blue-600 dark:text-blue-400 text-xs font-semibold">?</span>
                        </div>
                        <h4 className="text-sm font-semibold text-blue-900 dark:text-blue-100">
                          Co to jest „głosowanie kworum"?
                        </h4>
                      </div>
                      <p className="text-xs text-blue-800 dark:text-blue-200 leading-relaxed">
                        Głosowanie kworum to techniczne głosowanie w Sejmie, które sprawdza, ilu posłów jest obecnych na sali i może głosować. 
                        Nie dotyczy żadnej ustawy ani decyzji politycznej — jego jedynym celem jest policzenie obecnych posłów, 
                        żeby upewnić się, że Sejm może legalnie głosować nad kolejnymi punktami obrad.
                      </p>
                    </div>
                  )}
                  
                  {/* Definicja dla wniosków o odroczenie posiedzenia */}
                  {bill.description?.toLowerCase().includes('wniosek o odroczenie posiedzenia') && (
                    <div className="mb-4 p-3 bg-gradient-to-r from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 border border-orange-200 dark:border-orange-800 rounded-lg">
                      <div className="flex items-center mb-2">
                        <div className="w-6 h-6 bg-orange-100 dark:bg-orange-800 rounded-full flex items-center justify-center mr-2">
                          <span className="text-orange-600 dark:text-orange-400 text-xs font-semibold">?</span>
                        </div>
                        <h4 className="text-sm font-semibold text-orange-900 dark:text-orange-100">
                          Co to jest „wniosek o odroczenie posiedzenia"?
                        </h4>
                      </div>
                      <p className="text-xs text-orange-800 dark:text-orange-200 leading-relaxed">
                        Wniosek o odroczenie posiedzenia to propozycja przerwania obrad Sejmu i przełożenia ich na inny termin. 
                        Taki wniosek może złożyć poseł, klub parlamentarny lub marszałek Sejmu, gdy uznają, że obrady nie mogą 
                        lub nie powinny być kontynuowane w danym momencie.
                      </p>
                    </div>
                  )}
                  
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
                  
                  </div>
                  
                  <div className="mt-auto">
                    <div className="flex items-center justify-end text-sm text-gray-500 dark:text-gray-400 mb-3">
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
