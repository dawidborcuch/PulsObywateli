import { useState } from 'react'
import Head from 'next/head'
import Layout from '@/components/Layout'
import Hero from '@/components/Hero'
import FeaturedBills from '@/components/FeaturedBills'
import FeaturedPolls from '@/components/FeaturedPolls'
import Stats from '@/components/Stats'

export default function Home() {
  const [activeTab, setActiveTab] = useState<'bills' | 'polls'>('bills')

  return (
    <>
      <Head>
        <title>PulsObywateli - Obywatelska platforma sondażowo-informacyjna</title>
        <meta name="description" content="Śledź projekty ustaw, głosuj w sondażach i wyrażaj swoją opinię na temat polityki w Polsce" />
      </Head>
      
      <Layout>
        <Hero />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="mb-8">
            <div className="border-b border-gray-200 dark:border-gray-700">
              <nav className="-mb-px flex space-x-8">
                <button
                  onClick={() => setActiveTab('bills')}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'bills'
                      ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  Projekty ustaw
                </button>
                <button
                  onClick={() => setActiveTab('polls')}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'polls'
                      ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  Sondaże
                </button>
              </nav>
            </div>
          </div>
          
          {activeTab === 'bills' && <FeaturedBills />}
          {activeTab === 'polls' && <FeaturedPolls />}
        </div>
        
        <Stats />
      </Layout>
    </>
  )
}

