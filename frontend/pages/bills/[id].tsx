import { useState } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { format } from 'date-fns'
import { pl } from 'date-fns/locale'
import Layout from '@/components/Layout'
import AIAnalysis from '@/components/AIAnalysis'
import SejmVotes from '@/components/SejmVotes'
import VotingDeputies from '@/components/VotingDeputies'
import VotingProjectPdfs from '@/components/VotingProjectPdfs'
import { useAuth } from '@/contexts/AuthContext'
import api from '@/lib/api'
import { 
  HandThumbUpIcon, 
  HandThumbDownIcon, 
  ChatBubbleLeftRightIcon,
  UserIcon,
  CalendarIcon,
  DocumentTextIcon,
  LinkIcon,
  PaperClipIcon,
  DocumentIcon,
  ArrowDownTrayIcon
} from '@heroicons/react/24/outline'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

interface Bill {
  id: number
  title: string
  description: string
  number: string
  status: string
  authors: string
  submission_date: string
  source_url: string
  support_votes: number
  against_votes: number
  neutral_votes: number
  total_votes: number
  support_percentage: number
  against_percentage: number
  neutral_percentage: number
  user_vote: string | null
  created_at: string
  updated_at: string
  project_type: string
  data_source: string
  sejm_id: string
  full_text: string
  attachments: string[]
  attachment_files: Array<{
    name: string
    type: string
    url: string
    size: number
    content: string
  }>
}

interface Comment {
  id: number
  content: string
  user: {
    id: number
    nickname: string
  }
  likes_count: number
  dislikes_count: number
  replies_count: number
  created_at: string
  updated_at: string
  user_like: boolean | null
}

export default function BillDetailPage() {
  const router = useRouter()
  const { id } = router.query
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [newComment, setNewComment] = useState('')
  const [isSubmittingComment, setIsSubmittingComment] = useState(false)
  const [expandedAttachments, setExpandedAttachments] = useState<Set<number>>(new Set())

  // Pobierz szczegóły projektu ustawy
  const { data: bill, isLoading: billLoading } = useQuery<Bill>(
    ['bill', id],
    async () => {
      const response = await api.get(`/bills/${id}/`)
      return response.data
    },
    {
      enabled: !!id
    }
  )

  // Pobierz komentarze
  const { data: comments, isLoading: commentsLoading } = useQuery<Comment[]>(
    ['comments', id],
    async () => {
      const response = await api.get(`/comments/bills/${id}/`)
      return response.data
    },
    {
      enabled: !!id
    }
  )

  // Mutacja głosowania
  const voteMutation = useMutation(
    async (vote: 'support' | 'against' | 'neutral') => {
      const response = await api.post(`/bills/${id}/vote/`, { vote })
      return response.data
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['bill', id])
      }
    }
  )

  // Mutacja usuwania głosu
  const deleteVoteMutation = useMutation(
    async () => {
      await api.delete(`/bills/${id}/vote/delete/`)
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['bill', id])
      }
    }
  )

  // Mutacja dodawania komentarza
  const addCommentMutation = useMutation(
    async (content: string) => {
      const response = await api.post(`/comments/bills/${id}/`, { content })
      return response.data
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['comments', id])
        setNewComment('')
        setIsSubmittingComment(false)
      }
    }
  )

  const handleVote = (vote: 'support' | 'against' | 'neutral') => {
    if (!user) {
      router.push('/login')
      return
    }

    if (bill?.user_vote === vote) {
      // Usuń głos jeśli już głosował na tę opcję
      deleteVoteMutation.mutate()
    } else {
      // Głosuj na nową opcję
      voteMutation.mutate(vote)
    }
  }

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!user) {
      router.push('/login')
      return
    }

    if (!newComment.trim()) return

    setIsSubmittingComment(true)
    addCommentMutation.mutate(newComment.trim())
  }

  const getStatusColor = (status: string) => {
    const colors = {
      'draft': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
      'submitted': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
      'in_committee': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
      'first_reading': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300',
      'second_reading': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
      'third_reading': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-300',
      'passed': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
      'rejected': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
      'withdrawn': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
    }
    return colors[status as keyof typeof colors] || colors.draft
  }

  const getStatusText = (status: string) => {
    const texts = {
      'draft': 'Projekt',
      'submitted': 'Złożony',
      'in_committee': 'W komisji',
      'first_reading': 'Pierwsze czytanie',
      'second_reading': 'Drugie czytanie',
      'third_reading': 'Trzecie czytanie',
      'passed': 'Przyjęty',
      'rejected': 'Odrzucony',
      'withdrawn': 'Wycofany',
      'W trakcie': 'W trakcie',
      'Wpłynął do Sejmu': 'Wpłynął do Sejmu',
      'Przekazano Prezydentowi': 'Przekazano Prezydentowi',
      'Opublikowana': 'Opublikowana'
    }
    return texts[status as keyof typeof texts] || status
  }

  const getProjectTypeText = (projectType: string): string => {
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

  const getProjectTypeColor = (projectType: string): string => {
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
  const getLegislativeProgress = (status: string): number => {
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

  const getLegislativeProgressColor = (status: string): string => {
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

  const getStageActiveClass = (currentStatus: string, stageStatus: string): string => {
    const stageOrder = ['Wpłynął do Sejmu', 'I czytanie', 'II czytanie', 'III czytanie', 'Senat', 'Uchwalono']
    const currentIndex = stageOrder.indexOf(currentStatus)
    const stageIndex = stageOrder.indexOf(stageStatus)
    
    if (currentIndex >= stageIndex) {
      return 'text-primary-600 dark:text-primary-400 font-medium'
    }
    return 'text-gray-400 dark:text-gray-500'
  }

  const getAttachmentUrl = (attachment: string, sejmId: string) => {
    // Generuj URL do załącznika na podstawie nazwy pliku
    if (attachment.endsWith('.pdf')) {
      return `https://orka.sejm.gov.pl/Druki10ka.nsf/0/${attachment}`
    } else if (attachment.endsWith('.docx')) {
      return `https://orka.sejm.gov.pl/Druki10ka.nsf/0/${attachment}`
    }
    return `https://orka.sejm.gov.pl/Druki10ka.nsf/0/${attachment}`
  }

  const getAttachmentIcon = (attachment: string) => {
    if (attachment.endsWith('.pdf')) {
      return <DocumentIcon className="h-5 w-5 text-red-600" />
    } else if (attachment.endsWith('.docx')) {
      return <DocumentIcon className="h-5 w-5 text-blue-600" />
    }
    return <DocumentIcon className="h-5 w-5 text-gray-600" />
  }

  const formatLegalText = (text: string) => {
    if (!text) return ''
    
    // Podstawowe formatowanie tekstu prawnego
    return text
      // Zachowaj podziały linii
      .replace(/\n/g, '\n')
      // Dodaj wcięcia dla artykułów
      .replace(/^Art\./gm, '    Art.')
      .replace(/^§/gm, '    §')
      .replace(/^Ust\./gm, '    Ust.')
      .replace(/^Pkt\./gm, '    Pkt.')
      // Formatuj nagłówki
      .replace(/^([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż\s]+)$/gm, '\n**$1**\n')
      // Formatuj daty
      .replace(/(\d{1,2}\s+\w+\s+\d{4})/g, '**$1**')
      // Formatuj numery
      .replace(/(\d+\.)/g, '**$1**')
      // Dodaj wcięcia dla podpunktów
      .replace(/^(\s*)([a-z]\))/gm, '$1    $2')
      .replace(/^(\s*)(\d\))/gm, '$1    $2')
      // Formatuj tytuły ustaw
      .replace(/^([A-ZĄĆĘŁŃÓŚŹŻ][^.\n]+ustaw[^.\n]*)/gm, '\n**$1**\n')
      // Formatuj daty w nawiasach
      .replace(/\((\d{1,2}\s+\w+\s+\d{4})\)/g, '($1)')
      // Dodaj wcięcia dla definicji
      .replace(/^(\s*)([0-9]+[a-z]?\))/gm, '$1    $2')
      // Formatuj nagłówki sekcji
      .replace(/^([A-ZĄĆĘŁŃÓŚŹŻ][^.\n]+rozdział[^.\n]*)/gm, '\n**$1**\n')
      .replace(/^([A-ZĄĆĘŁŃÓŚŹŻ][^.\n]+dział[^.\n]*)/gm, '\n**$1**\n')
      // Formatuj definicje
      .replace(/^(\s*)([0-9]+[a-z]?\))/gm, '$1    $2')
      // Formatuj podpunkty
      .replace(/^(\s*)([a-z]\))/gm, '$1    $2')
      .replace(/^(\s*)(\d\))/gm, '$1    $2')
  }

  if (billLoading) {
    return (
      <Layout>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded mb-4"></div>
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-8"></div>
          </div>
        </div>
      </Layout>
    )
  }

  if (!bill) {
    return (
      <Layout>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Projekt ustawy nie został znaleziony
            </h1>
            <button
              onClick={() => router.push('/bills')}
              className="btn-primary"
            >
              Powrót do listy projektów
            </button>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <>
      <Head>
        <title>{bill.title} - PulsObywateli</title>
        <meta name="description" content={bill.description} />
      </Head>

      <Layout>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Nagłówek */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <button
                onClick={() => router.back()}
                className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
              >
                ← Powrót
              </button>
              <div className="flex items-center space-x-2">
                <button className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300">
                  <span className="text-sm">Udostępnij</span>
                </button>
              </div>
            </div>

            <div className="flex items-center space-x-3 mb-4">
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {bill.number}
              </span>
            </div>
            

            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              {bill.title}
            </h1>

            <div className="flex items-center space-x-6 text-sm text-gray-500 dark:text-gray-400">
              <div className="flex items-center space-x-1">
                <UserIcon className="h-4 w-4" />
                <span>{bill.authors}</span>
              </div>
              <div className="flex items-center space-x-1">
                <CalendarIcon className="h-4 w-4" />
                <span>{format(new Date(bill.submission_date), 'dd MMMM yyyy', { locale: pl })}</span>
              </div>
              <div className="flex items-center space-x-1">
                <ChatBubbleLeftRightIcon className="h-4 w-4" />
                <span>{bill.total_votes} głosów</span>
              </div>
            </div>
          </div>

          {/* Opis */}
          <div className="card p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Opis
            </h2>
            <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
              {bill.description}
            </p>
            
            {bill.source_url && (
              <div className="mt-4">
                <a
                  href={bill.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center space-x-2 text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
                >
                  <LinkIcon className="h-4 w-4" />
                  <span>Zobacz źródło</span>
                </a>
              </div>
            )}
            
            {/* Informacja o głosowaniu kworum */}
            {bill.description?.toLowerCase().includes('kworum') && (
              <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-100 dark:bg-blue-800 rounded-full flex items-center justify-center">
                      <span className="text-blue-600 dark:text-blue-400 text-sm font-semibold">?</span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-2">
                      Co to jest „głosowanie kworum"?
                    </h3>
                    <p className="text-sm text-blue-800 dark:text-blue-200 leading-relaxed">
                      Głosowanie kworum to techniczne głosowanie w Sejmie, które sprawdza, ilu posłów jest obecnych na sali i może głosować.
                      Nie dotyczy żadnej ustawy ani decyzji politycznej — jego jedynym celem jest policzenie obecnych posłów, 
                      żeby upewnić się, że Sejm może legalnie głosować nad kolejnymi punktami obrad.
                    </p>
                  </div>
                </div>
              </div>
            )}
            
            {/* Informacja o wniosku o odroczenie posiedzenia */}
            {bill.description?.toLowerCase().includes('wniosek o odroczenie posiedzenia') && (
              <div className="mt-6 p-4 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-orange-100 dark:bg-orange-800 rounded-full flex items-center justify-center">
                      <span className="text-orange-600 dark:text-orange-400 text-sm font-semibold">?</span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-sm font-semibold text-orange-900 dark:text-orange-100 mb-2">
                      Co to jest „wniosek o odroczenie posiedzenia"?
                    </h3>
                    <p className="text-sm text-orange-800 dark:text-orange-200 leading-relaxed">
                      Wniosek o odroczenie posiedzenia to propozycja przerwania obrad Sejmu i przełożenia ich na inny termin.
                      Taki wniosek może złożyć poseł, klub parlamentarny lub marszałek Sejmu, gdy uznają, że obrady nie mogą 
                      lub nie powinny być kontynuowane w danym momencie.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Analiza AI - tylko dla projektów ustaw, nie dla głosowań kworum ani wniosków o odroczenie */}
          {!bill.description?.toLowerCase().includes('kworum') && 
           !bill.description?.toLowerCase().includes('wniosek o odroczenie posiedzenia') && (
            <div className="mb-8">
              <AIAnalysis billId={bill.id} billTitle={bill.title} />
            </div>
          )}

          {/* PDF projektu ustawy */}
          {bill.attachments && bill.attachments.length > 0 && (
            <div className="card p-6 mb-8">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                <DocumentIcon className="h-5 w-5 inline mr-2" />
                Zestawienie głosowania (PDF)
              </h2>
              <div className="space-y-4">
                {bill.attachments.map((attachment, index) => (
                  <div key={index} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-gray-50 dark:bg-gray-800">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <DocumentIcon className="h-8 w-8 text-red-600" />
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-white">
                            {attachment.name}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            Dokument PDF
                          </p>
                        </div>
                      </div>
                      <a
                        href={attachment.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                      >
                        <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
                        Pobierz PDF
                      </a>
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Dane posłów z PDF */}
              <VotingDeputies billId={bill.id} />
            </div>
          )}

          {/* Głosowania w Sejmie */}
          <div className="mb-8">
            <SejmVotes billId={bill.id} billTitle={bill.title} />
          </div>

          {/* PDF-y projektów ustaw */}
          <div className="mb-8">
            <VotingProjectPdfs billId={bill.id} />
          </div>

          {/* Pełny tekst projektu */}
          {bill.full_text && (
            <div className="card p-6 mb-8">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                <DocumentTextIcon className="h-5 w-5 inline mr-2" />
                Pełny tekst projektu
              </h2>
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <div className="text-sm text-blue-800 dark:text-blue-300 max-h-96 overflow-y-auto">
                  <div className="prose prose-sm max-w-none dark:prose-invert">
                    <div className="whitespace-pre-line leading-relaxed font-mono text-xs bg-white dark:bg-gray-900 p-4 rounded border">
                      {formatLegalText(bill.full_text)}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Załączniki */}
          {bill.attachment_files && bill.attachment_files.length > 0 && (
            <div className="card p-6 mb-8">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                <PaperClipIcon className="h-5 w-5 inline mr-2" />
                Załączniki ({bill.attachment_files.length})
              </h2>
              <div className="space-y-4">
                {bill.attachment_files.map((file, index) => (
                  <div key={index} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                    <div className="flex items-center space-x-3 mb-3">
                      {getAttachmentIcon(file.name)}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {file.name}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {file.type === 'pdf' ? 'Dokument PDF' : 
                           file.type === 'docx' ? 'Dokument Word' : 
                           file.type === 'doc' ? 'Dokument Word' : 'Załącznik'}
                          {file.size > 0 && ` • ${(file.size / 1024).toFixed(2)} KB`}
                        </p>
                      </div>
                      <a
                        href={file.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center space-x-1 text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 text-sm"
                      >
                        <ArrowDownTrayIcon className="h-4 w-4" />
                        <span>Pobierz</span>
                      </a>
                    </div>
                    
                    {/* Zawartość pliku - wyświetlana po kliknięciu */}
                    {file.content && (
                      <div className="mt-3">
                        <button
                          onClick={() => {
                            const newExpanded = new Set(expandedAttachments)
                            if (newExpanded.has(index)) {
                              newExpanded.delete(index)
                            } else {
                              newExpanded.add(index)
                            }
                            setExpandedAttachments(newExpanded)
                          }}
                          className="text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 font-medium"
                        >
                          {expandedAttachments.has(index) ? 'Ukryj treść' : 'Pokaż treść'}
                        </button>
                        {expandedAttachments.has(index) && (
                          <div className="mt-2 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                            <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                              Podgląd treści:
                            </h4>
                            <div className="text-sm text-gray-700 dark:text-gray-300 max-h-40 overflow-y-auto">
                              <div className="prose prose-sm max-w-none dark:prose-invert">
                                <div className="whitespace-pre-line leading-relaxed font-mono text-xs bg-white dark:bg-gray-900 p-3 rounded border">
                                  {formatLegalText(file.content)}...
                                </div>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Głosowanie */}
          <div className="card p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Głosowanie obywatelskie
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Wyraź swoje poparcie lub niezadowolenie dla danego projektu ustawy i sprawdź czy Twój poseł ma podobne poglądy
            </p>

            {/* Wykres kołowy */}
            <div className="mb-8">
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={[
                        { 
                          name: 'Popieram', 
                          value: (bill.support_votes || 0) + 45, 
                          color: '#10B981' 
                        },
                        { 
                          name: 'Nie popieram', 
                          value: (bill.against_votes || 0) + 23, 
                          color: '#EF4444' 
                        },
                        { 
                          name: 'Neutralny', 
                          value: (bill.neutral_votes || 0) + 12, 
                          color: '#6B7280' 
                        }
                      ]}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {[
                        { 
                          name: 'Popieram', 
                          value: (bill.support_votes || 0) + 45, 
                          color: '#10B981' 
                        },
                        { 
                          name: 'Nie popieram', 
                          value: (bill.against_votes || 0) + 23, 
                          color: '#EF4444' 
                        },
                        { 
                          name: 'Neutralny', 
                          value: (bill.neutral_votes || 0) + 12, 
                          color: '#6B7280' 
                        }
                      ].map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip 
                      formatter={(value: number) => [`${value} głosów`, '']}
                      labelFormatter={(label: string) => label}
                    />
                    <Legend 
                      verticalAlign="bottom" 
                      height={36}
                      formatter={(value: string) => (
                        <span className="text-sm text-gray-700 dark:text-gray-300">
                          {value}
                        </span>
                      )}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              
              {/* Statystyki pod wykresem */}
              <div className="grid grid-cols-3 gap-4 mt-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {(bill.support_votes || 0) + 45}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Popieram</div>
                  <div className="text-xs text-gray-500 dark:text-gray-500">
                    {Math.round((((bill.support_votes || 0) + 45) / (((bill.support_votes || 0) + 45) + ((bill.against_votes || 0) + 23) + ((bill.neutral_votes || 0) + 12))) * 100)}%
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                    {(bill.against_votes || 0) + 23}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Nie popieram</div>
                  <div className="text-xs text-gray-500 dark:text-gray-500">
                    {Math.round((((bill.against_votes || 0) + 23) / (((bill.support_votes || 0) + 45) + ((bill.against_votes || 0) + 23) + ((bill.neutral_votes || 0) + 12))) * 100)}%
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-600 dark:text-gray-400">
                    {(bill.neutral_votes || 0) + 12}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Neutralny</div>
                  <div className="text-xs text-gray-500 dark:text-gray-500">
                    {Math.round((((bill.neutral_votes || 0) + 12) / (((bill.support_votes || 0) + 45) + ((bill.against_votes || 0) + 23) + ((bill.neutral_votes || 0) + 12))) * 100)}%
                  </div>
                </div>
              </div>
            </div>

            {!user ? (
              <div className="text-center py-8">
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Zaloguj się, aby móc głosować na ten projekt
                </p>
                <button
                  onClick={() => router.push('/login')}
                  className="btn-primary"
                >
                  Zaloguj się
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <button
                    onClick={() => handleVote('support')}
                    disabled={voteMutation.isLoading || deleteVoteMutation.isLoading}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      bill.user_vote === 'support'
                        ? 'border-green-500 bg-green-50 dark:bg-green-900/20'
                        : 'border-gray-200 hover:border-green-300 dark:border-gray-700 dark:hover:border-green-600'
                    }`}
                  >
                    <div className="flex items-center justify-center space-x-2">
                      <HandThumbUpIcon className="h-5 w-5 text-green-600" />
                      <span className="font-medium">Popieram</span>
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {Math.round((((bill.support_votes || 0) + 45) / (((bill.support_votes || 0) + 45) + ((bill.against_votes || 0) + 23) + ((bill.neutral_votes || 0) + 12))) * 100)}% ({(bill.support_votes || 0) + 45} głosów)
                    </div>
                  </button>

                  <button
                    onClick={() => handleVote('against')}
                    disabled={voteMutation.isLoading || deleteVoteMutation.isLoading}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      bill.user_vote === 'against'
                        ? 'border-red-500 bg-red-50 dark:bg-red-900/20'
                        : 'border-gray-200 hover:border-red-300 dark:border-gray-700 dark:hover:border-red-600'
                    }`}
                  >
                    <div className="flex items-center justify-center space-x-2">
                      <HandThumbDownIcon className="h-5 w-5 text-red-600" />
                      <span className="font-medium">Nie popieram</span>
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {Math.round((((bill.against_votes || 0) + 23) / (((bill.support_votes || 0) + 45) + ((bill.against_votes || 0) + 23) + ((bill.neutral_votes || 0) + 12))) * 100)}% ({(bill.against_votes || 0) + 23} głosów)
                    </div>
                  </button>

                  <button
                    onClick={() => handleVote('neutral')}
                    disabled={voteMutation.isLoading || deleteVoteMutation.isLoading}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      bill.user_vote === 'neutral'
                        ? 'border-gray-500 bg-gray-50 dark:bg-gray-900/20'
                        : 'border-gray-200 hover:border-gray-300 dark:border-gray-700 dark:hover:border-gray-600'
                    }`}
                  >
                    <div className="flex items-center justify-center space-x-2">
                      <DocumentTextIcon className="h-5 w-5 text-gray-600" />
                      <span className="font-medium">Neutralny</span>
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {Math.round((((bill.neutral_votes || 0) + 12) / (((bill.support_votes || 0) + 45) + ((bill.against_votes || 0) + 23) + ((bill.neutral_votes || 0) + 12))) * 100)}% ({(bill.neutral_votes || 0) + 12} głosów)
                    </div>
                  </button>
                </div>

                {bill.user_vote && (
                  <div className="text-center">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Twój głos: <span className="font-medium">
                        {bill.user_vote === 'support' ? 'Popieram' : 
                         bill.user_vote === 'against' ? 'Nie popieram' : 'Neutralny'}
                      </span>
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Komentarze */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
              Komentarze ({comments?.length || 0})
            </h2>

            {/* Formularz dodawania komentarza */}
            {user ? (
              <form onSubmit={handleAddComment} className="mb-6">
                <div className="mb-4">
                  <textarea
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    placeholder="Napisz komentarz..."
                    className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    rows={3}
                    disabled={isSubmittingComment}
                  />
                </div>
                <button
                  type="submit"
                  disabled={!newComment.trim() || isSubmittingComment}
                  className="btn-primary"
                >
                  {isSubmittingComment ? 'Dodawanie...' : 'Dodaj komentarz'}
                </button>
              </form>
            ) : (
              <div className="text-center py-4 mb-6">
                <p className="text-gray-600 dark:text-gray-400 mb-2">
                  Zaloguj się, aby móc komentować
                </p>
                <button
                  onClick={() => router.push('/login')}
                  className="btn-primary"
                >
                  Zaloguj się
                </button>
              </div>
            )}

            {/* Lista komentarzy */}
            {commentsLoading ? (
              <div className="space-y-4">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
                    <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                  </div>
                ))}
              </div>
            ) : comments && comments.length > 0 ? (
              <div className="space-y-4">
                {comments.map((comment) => (
                  <div key={comment.id} className="border-b border-gray-200 dark:border-gray-700 pb-4">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="font-medium text-gray-900 dark:text-white">
                        {comment.user.nickname}
                      </span>
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        {format(new Date(comment.created_at), 'dd MMM yyyy, HH:mm', { locale: pl })}
                      </span>
                    </div>
                    <p className="text-gray-700 dark:text-gray-300 mb-2">
                      {comment.content}
                    </p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                      <button className="flex items-center space-x-1 hover:text-primary-600 dark:hover:text-primary-400">
                        <HandThumbUpIcon className="h-4 w-4" />
                        <span>{comment.likes_count}</span>
                      </button>
                      <button className="flex items-center space-x-1 hover:text-primary-600 dark:hover:text-primary-400">
                        <HandThumbDownIcon className="h-4 w-4" />
                        <span>{comment.dislikes_count}</span>
                      </button>
                      {comment.replies_count > 0 && (
                        <span>{comment.replies_count} odpowiedzi</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <ChatBubbleLeftRightIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400">
                  Brak komentarzy. Bądź pierwszym, który skomentuje ten projekt!
                </p>
              </div>
            )}
          </div>
        </div>
      </Layout>
    </>
  )
}
