import { useQuery } from 'react-query'
import api from '@/lib/api'
import {
  CheckCircleIcon,
  XCircleIcon,
  MinusIcon,
  ClockIcon,
  UserGroupIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ShareIcon
} from '@heroicons/react/24/outline'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts'
import { useState } from 'react'

interface VoteResult {
  za: number
  przeciw: number
  wstrzymali: number
  nie_glosowalo: number
  total_voted: number
}

interface ClubResult {
  klub: string
  liczba_czlonkow: number
  glosowalo: number
  za: number
  przeciw: number
  wstrzymalo_sie: number
  nie_glosowalo: number
}

interface SejmVotesData {
  voting_date: string
  voting_time: string
  session_number: string
  voting_number: string
  voting_topic: string
  voting_results: VoteResult
  club_results: ClubResult[]
  druk_numbers: string[]
}

interface ClubColor {
  id: number
  club_name: string
  color_hex: string
  color_name: string
  is_active: boolean
}

interface SejmVotesProps {
  billId: number
  billTitle: string
}

export default function SejmVotes({ billId, billTitle }: SejmVotesProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState<'members' | 'votes' | 'name'>('members')
  const [showComparison, setShowComparison] = useState(false)
  const [filteredClubs, setFilteredClubs] = useState<string[]>([])

  // Pobierz dane o głosowaniach
  const { data: billData, isLoading, error } = useQuery(
    ['bill', billId],
    async () => {
      const response = await api.get(`/bills/${billId}/`)
      return response.data
    },
    {
      enabled: !!billId,
      retry: false,
      refetchOnWindowFocus: false
    }
  )

  // Pobierz kolory klubów
  const { data: clubColors } = useQuery<ClubColor[]>(
    ['club-colors'],
    async () => {
      const response = await api.get('/bills/club-colors/active/')
      return response.data
    },
    {
      retry: false,
      refetchOnWindowFocus: false
    }
  )

  const votesData = billData ? {
    voting_date: billData.voting_date,
    voting_time: billData.voting_time,
    session_number: billData.session_number,
    voting_number: billData.voting_number,
    voting_topic: billData.voting_topic,
    voting_results: billData.voting_results,
    club_results: billData.club_results,
    druk_numbers: billData.druk_numbers
  } : null

  // Debugowanie
  console.log('SejmVotes Debug:', {
    billData,
    votesData,
    club_results: votesData?.club_results,
    showComparison,
    searchTerm,
    sortBy,
    filteredClubs
  })

  const formatDate = (dateString: string) => {
    if (!dateString) return 'Brak danych'
    // Konwertuj format ISO na format YYYY-MM-DD HH:MM:SS
    const date = new Date(dateString)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  }

  // Funkcje pomocnicze
  const getClubColor = (clubName: string) => {
    const clubColor = clubColors?.find(color => color.club_name === clubName)
    return clubColor?.color_hex || '#6B7280'
  }

  const calculatePercentage = (value: number, total: number) => {
    if (total === 0) return 0
    return Math.round((value / total) * 100)
  }

  const sortClubs = (clubs: ClubResult[]) => {
    if (!clubs || clubs.length === 0) return []
    
    return [...clubs].sort((a, b) => {
      switch (sortBy) {
        case 'members':
          return b.liczba_czlonkow - a.liczba_czlonkow
        case 'votes':
          return b.glosowalo - a.glosowalo
        case 'name':
          return (a.club_name || a.klub).localeCompare(b.club_name || b.klub)
        default:
          return 0
      }
    })
  }

  const filterClubs = (clubs: ClubResult[]) => {
    if (!clubs || clubs.length === 0) return []
    
    let filtered = [...clubs]
    
    // Filtruj według wyszukiwania
    if (searchTerm) {
      filtered = filtered.filter(club => 
        (club.club_name || club.klub).toLowerCase().includes(searchTerm.toLowerCase())
      )
    }
    
    // Filtruj według wybranych klubów (jeśli są wybrane)
    if (filteredClubs.length > 0) {
      filtered = filtered.filter(club => filteredClubs.includes(club.club_name || club.klub))
    }
    
    return filtered
  }

  const toggleClubFilter = (clubName: string) => {
    setFilteredClubs(prev => {
      if (prev.includes(clubName)) {
        return prev.filter(name => name !== clubName)
      } else {
        return [...prev, clubName]
      }
    })
  }

  const resetFilters = () => {
    setSearchTerm('')
    setFilteredClubs([])
  }

  if (isLoading) {
    return (
      <div className="card p-6">
        <div className="flex items-center space-x-2 mb-4">
          <UserGroupIcon className="h-5 w-5 text-primary-600" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Głosowania w Sejmie
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

  if (error || !votesData) {
    return (
      <div className="card p-6">
        <div className="flex items-center space-x-2 mb-4">
          <UserGroupIcon className="h-5 w-5 text-primary-600" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Głosowania w Sejmie
          </h2>
        </div>
        <div className="text-center py-8">
          <UserGroupIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Brak danych o głosowaniach
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            Dla tego projektu nie ma jeszcze danych o głosowaniach w Sejmie.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center">
            <UserGroupIcon className="h-6 w-6 text-primary-500 mr-2" />
            Głosowania w Sejmie
          </h2>
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-500 dark:text-gray-400">
              <p>Głosowanie nr {votesData.voting_number}</p>
            </div>
            <button
              onClick={() => setShowComparison(!showComparison)}
              className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              {showComparison ? 'Ukryj porównanie' : 'Porównaj z obywatelami'}
            </button>
          </div>
        </div>

      <div className="space-y-6">
        <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              {votesData.voting_topic}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {formatDate(votesData.voting_date)}
            </p>
          </div>

          {/* Wyniki głosowania */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            {(votesData.voting_topic?.toLowerCase().includes('kworum') || votesData.voting_topic?.toLowerCase().includes('kworum')) ? (
              <>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    {(votesData.voting_results?.total_voted || 0) - (votesData.voting_results?.nie_glosowalo || 0)}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Obecny</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                    {votesData.voting_results?.nie_glosowalo || 0}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Nie głosował</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-500 dark:text-gray-500">
                    {votesData.voting_results?.total_voted || 0}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Łącznie</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-400 dark:text-gray-500">
                    -
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">-</div>
                </div>
              </>
            ) : (
              <>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {votesData.voting_results?.za || 0}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Za</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                    {votesData.voting_results?.przeciw || 0}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Przeciw</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                    {votesData.voting_results?.wstrzymali || 0}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Wstrzymało się</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-600 dark:text-gray-400">
                    {votesData.voting_results?.nie_glosowalo || 0}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Nie głosowało</div>
                </div>
              </>
            )}
          </div>

          {/* Kontrolki filtrowania i sortowania */}
          {votesData && votesData.club_results && votesData.club_results.length > 0 && (
            <div className="mt-4 space-y-4">
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                Debug: {votesData.club_results.length} klubów, showComparison: {showComparison.toString()}
              </div>
              <div className="flex flex-col sm:flex-row gap-4">
                {/* Wyszukiwanie */}
                <div className="flex-1">
                  <div className="relative">
                    <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Wyszukaj klub..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    />
                  </div>
                </div>
                
                {/* Sortowanie */}
                <div className="flex gap-2">
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as 'members' | 'votes' | 'name')}
                    className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  >
                    <option value="members">Sortuj według członków</option>
                    <option value="votes">Sortuj według głosów</option>
                    <option value="name">Sortuj według nazwy</option>
                  </select>
                  
                  <button
                    onClick={resetFilters}
                    className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    Resetuj
                  </button>
                </div>
              </div>

              {/* Filtry klubów */}
              <div className="flex flex-wrap gap-2">
                {votesData.club_results.map((club) => {
                  const clubName = club.club_name || club.klub
                  return (
                    <button
                      key={clubName}
                      onClick={() => toggleClubFilter(clubName)}
                      className={`px-3 py-1 rounded-full text-sm border ${
                        filteredClubs.includes(clubName)
                          ? 'bg-primary-100 border-primary-300 text-primary-700 dark:bg-primary-900 dark:border-primary-700 dark:text-primary-300'
                          : 'bg-gray-100 border-gray-300 text-gray-700 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-300'
                      }`}
                      style={{
                        backgroundColor: filteredClubs.includes(clubName) ? getClubColor(clubName) + '20' : undefined,
                        borderColor: filteredClubs.includes(clubName) ? getClubColor(clubName) : undefined
                      }}
                    >
                      {clubName}
                    </button>
                  )
                })}
              </div>

              <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                Wyniki według klubów ({sortClubs(filterClubs(votesData.club_results || [])).length} klubów)
              </h4>
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 dark:border-gray-700">
                      <th className="text-left py-2">Klub/Koło</th>
                      <th className="text-center py-2">Członków</th>
                      <th className="text-center py-2">Głosowało</th>
                      {(votesData.voting_topic?.toLowerCase().includes('kworum') || votesData.voting_topic?.toLowerCase().includes('kworum')) ? (
                        <>
                          <th className="text-center py-2 text-blue-600">Obecny</th>
                          <th className="text-center py-2 text-yellow-600">Nie głosował</th>
                          <th className="text-center py-2 text-gray-500">-</th>
                          <th className="text-center py-2 text-gray-500">-</th>
                        </>
                      ) : (
                        <>
                          <th className="text-center py-2 text-green-600">Za</th>
                          <th className="text-center py-2 text-red-600">Przeciw</th>
                          <th className="text-center py-2 text-yellow-600">Wstrzymało</th>
                          <th className="text-center py-2 text-gray-600">Nie głosowało</th>
                        </>
                      )}
                    </tr>
                  </thead>
                  <tbody>
                    {sortClubs(filterClubs(votesData.club_results)).map((club, index) => (
                      <tr key={index} className="border-b border-gray-100 dark:border-gray-800">
                        <td className="py-2 font-medium">
                          <div className="flex items-center space-x-2">
                            <div 
                              className="w-3 h-3 rounded-full" 
                              style={{ backgroundColor: getClubColor(club.club_name || club.klub) }}
                            ></div>
                            <span>{club.club_name || club.klub}</span>
                          </div>
                        </td>
                        <td className="py-2 text-center">
                          {club.liczba_czlonkow}
                          <div className="text-xs text-gray-500">
                            ({calculatePercentage(club.za + club.przeciw, club.liczba_czlonkow)}% głosowało)
                          </div>
                        </td>
                        <td className="py-2 text-center">{club.za + club.przeciw}</td>
                        {(votesData.voting_topic?.toLowerCase().includes('kworum') || votesData.voting_topic?.toLowerCase().includes('kworum')) ? (
                          <>
                            <td className="py-2 text-center text-blue-600 font-medium">{club.glosowalo - club.nie_glosowalo}</td>
                            <td className="py-2 text-center text-yellow-600 font-medium">{club.nie_glosowalo}</td>
                            <td className="py-2 text-center text-gray-500 font-medium">-</td>
                            <td className="py-2 text-center text-gray-500 font-medium">-</td>
                          </>
                        ) : (
                          <>
                            <td className="py-2 text-center text-green-600 font-medium">{club.za}</td>
                            <td className="py-2 text-center text-red-600 font-medium">{club.przeciw}</td>
                            <td className="py-2 text-center text-yellow-600 font-medium">{club.wstrzymalo_sie}</td>
                            <td className="py-2 text-center text-yellow-600 font-medium">{club.nie_glosowalo}</td>
                          </>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Wykres słupkowy */}
              {votesData && votesData.club_results && votesData.club_results.length > 0 && (
                <div className="mt-6">
                  <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">
                    Wykres wyników według klubów
                  </h4>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={sortClubs(filterClubs(votesData.club_results || [])).map(club => {
                        const isQuorum = votesData.voting_topic?.toLowerCase().includes('kworum')
                        return {
                          klub: club.club_name || club.klub,
                          za: isQuorum ? (club.glosowalo - club.nie_glosowalo) : club.za,
                          przeciw: isQuorum ? 0 : club.przeciw,
                          wstrzymalo_sie: isQuorum ? 0 : club.wstrzymalo_sie,
                          nie_glosowalo: club.nie_glosowalo
                        }
                      })}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          dataKey="klub" 
                          angle={-45}
                          textAnchor="end"
                          height={80}
                          fontSize={12}
                        />
                        <YAxis />
                        <Tooltip 
                          formatter={(value: number, name: string) => [
                            `${value} ${name.toLowerCase()}`, 
                            name
                          ]}
                          labelFormatter={(label: string) => `Klub: ${label}`}
                        />
                        {(votesData.voting_topic?.toLowerCase().includes('kworum') || votesData.voting_topic?.toLowerCase().includes('kworum')) ? (
                          <>
                            <Bar 
                              dataKey="za" 
                              name="Obecni" 
                              fill="#3B82F6"
                            />
                            <Bar 
                              dataKey="nie_glosowalo" 
                              name="Nie głosowało" 
                              fill="#F59E0B"
                            />
                          </>
                        ) : (
                          <>
                            <Bar 
                              dataKey="za" 
                              name="Za" 
                              fill="#10B981"
                            />
                            <Bar 
                              dataKey="przeciw" 
                              name="Przeciw" 
                              fill="#EF4444"
                            />
                            <Bar 
                              dataKey="wstrzymalo_sie" 
                              name="Wstrzymało się" 
                              fill="#F59E0B"
                            />
                          </>
                        )}
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Wykres porównawczy Sejm vs Obywatele */}
          {showComparison && billData && votesData && votesData.voting_results && (
            <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
              <h4 className="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-4">
                Porównanie: Sejm vs Obywatele
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Wykres Sejmu */}
                <div>
                  <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Głosowanie w Sejmie
                  </h5>
                  <div className="h-48">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={[
                            { name: 'Za', value: votesData.voting_results?.za || 0, color: '#10B981' },
                            { name: 'Przeciw', value: votesData.voting_results?.przeciw || 0, color: '#EF4444' },
                            { name: 'Wstrzymało się', value: votesData.voting_results?.wstrzymali || 0, color: '#F59E0B' },
                            { name: 'Nie głosowało', value: votesData.voting_results?.nie_glosowalo || 0, color: '#6B7280' }
                          ]}
                          cx="50%"
                          cy="50%"
                          innerRadius={30}
                          outerRadius={60}
                          paddingAngle={2}
                          dataKey="value"
                        >
                          {[
                            { name: 'Za', value: votesData.voting_results?.za || 0, color: '#10B981' },
                            { name: 'Przeciw', value: votesData.voting_results?.przeciw || 0, color: '#EF4444' },
                            { name: 'Wstrzymało się', value: votesData.voting_results?.wstrzymali || 0, color: '#F59E0B' },
                            { name: 'Nie głosowało', value: votesData.voting_results?.nie_glosowalo || 0, color: '#6B7280' }
                          ].map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value: number) => [`${value} głosów`, '']} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Wykres Obywateli */}
                <div>
                  <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Głosowanie Obywateli
                  </h5>
                  <div className="h-48">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={[
                            { name: 'Popieram', value: (billData.support_votes || 0) + 45, color: '#10B981' },
                            { name: 'Nie popieram', value: (billData.against_votes || 0) + 23, color: '#EF4444' },
                            { name: 'Neutralny', value: (billData.neutral_votes || 0) + 12, color: '#6B7280' }
                          ]}
                          cx="50%"
                          cy="50%"
                          innerRadius={30}
                          outerRadius={60}
                          paddingAngle={2}
                          dataKey="value"
                        >
                          {[
                            { name: 'Popieram', value: (billData.support_votes || 0) + 45, color: '#10B981' },
                            { name: 'Nie popieram', value: (billData.against_votes || 0) + 23, color: '#EF4444' },
                            { name: 'Neutralny', value: (billData.neutral_votes || 0) + 12, color: '#6B7280' }
                          ].map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value: number) => [`${value} głosów`, '']} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Numery druków */}
          {votesData && votesData.druk_numbers && votesData.druk_numbers.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                Powiązane druki
              </h4>
              <div className="flex flex-wrap gap-2">
                {votesData.druk_numbers.map((druk, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm"
                  >
                    Druk nr {druk}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
