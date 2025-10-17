import { useQuery } from 'react-query'
import api from '@/lib/api'
import {
  CheckCircleIcon,
  XCircleIcon,
  MinusIcon,
  ClockIcon,
  UserGroupIcon
} from '@heroicons/react/24/outline'

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

interface SejmVotesProps {
  billId: number
  billTitle: string
}

export default function SejmVotes({ billId, billTitle }: SejmVotesProps) {
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

  const formatDate = (dateString: string) => {
    if (!dateString) return 'Brak danych'
    return dateString // Data już w formacie polskim
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
          <div className="text-sm text-gray-500 dark:text-gray-400">
            <p>Głosowanie nr {votesData.voting_number}</p>
          </div>
        </div>

      <div className="space-y-6">
        <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              {votesData.voting_topic}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {formatDate(votesData.voting_date)} o {votesData.voting_time}
            </p>
          </div>

          {/* Wyniki głosowania */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
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
          </div>

          {/* Wyniki według klubów */}
          {votesData.club_results && votesData.club_results.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                Wyniki według klubów
              </h4>
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 dark:border-gray-700">
                      <th className="text-left py-2">Klub/Koło</th>
                      <th className="text-center py-2">Członków</th>
                      <th className="text-center py-2">Głosowało</th>
                      <th className="text-center py-2 text-green-600">Za</th>
                      <th className="text-center py-2 text-red-600">Przeciw</th>
                      <th className="text-center py-2 text-yellow-600">Wstrzymało</th>
                      <th className="text-center py-2 text-gray-600">Nie głosowało</th>
                    </tr>
                  </thead>
                  <tbody>
                    {votesData.club_results.map((club, index) => (
                      <tr key={index} className="border-b border-gray-100 dark:border-gray-800">
                        <td className="py-2 font-medium">{club.klub}</td>
                        <td className="py-2 text-center">{club.liczba_czlonkow}</td>
                        <td className="py-2 text-center">{club.glosowalo}</td>
                        <td className="py-2 text-center text-green-600 font-medium">{club.za}</td>
                        <td className="py-2 text-center text-red-600 font-medium">{club.przeciw}</td>
                        <td className="py-2 text-center text-yellow-600 font-medium">{club.wstrzymalo_sie}</td>
                        <td className="py-2 text-center text-gray-600 font-medium">{club.nie_glosowalo}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Numery druków */}
          {votesData.druk_numbers && votesData.druk_numbers.length > 0 && (
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
