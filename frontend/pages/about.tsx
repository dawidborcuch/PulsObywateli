import Head from 'next/head'
import Layout from '@/components/Layout'
import { 
  HeartIcon, 
  ShieldCheckIcon, 
  ChartBarIcon, 
  UsersIcon,
  LightBulbIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline'

export default function AboutPage() {
  const features = [
    {
      icon: ChartBarIcon,
      title: 'Projekty ustaw',
      description: 'Śledź i głosuj na projekty ustaw w Polsce. Zobacz jak inni obywatele oceniają propozycje zmian prawnych.'
    },
    {
      icon: UsersIcon,
      title: 'Sondaże społeczne',
      description: 'Wyrażaj swoją opinię w sondażach dotyczących polityki, społeczeństwa i gospodarki.'
    },
    {
      icon: ShieldCheckIcon,
      title: 'Transparentność',
      description: 'Wszystkie dane pochodzą z oficjalnych źródeł. Głosowanie jest anonimowe i bezpieczne.'
    },
    {
      icon: LightBulbIcon,
      title: 'Świadomość obywatelska',
      description: 'Buduj świadomość obywatelską poprzez aktywne uczestnictwo w demokracji.'
    }
  ]

  const stats = [
    { label: 'Projekty ustaw', value: '100+' },
    { label: 'Aktywne sondaże', value: '50+' },
    { label: 'Użytkownicy', value: '1000+' },
    { label: 'Oddane głosy', value: '10,000+' }
  ]

  return (
    <>
      <Head>
        <title>O projekcie - PulsObywateli</title>
        <meta name="description" content="Poznaj PulsObywateli - obywatelską platformę sondażowo-informacyjną" />
      </Head>
      
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Hero section */}
          <div className="text-center mb-16">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-6">
              O PulsObywateli
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
              Obywatelska platforma sondażowo-informacyjna do śledzenia projektów ustaw 
              i wyrażania opinii na temat polityki w Polsce
            </p>
          </div>

          {/* Misja */}
          <div className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-2xl p-8 mb-16 text-white">
            <div className="max-w-4xl mx-auto text-center">
              <HeartIcon className="h-16 w-16 mx-auto mb-6 text-primary-200" />
              <h2 className="text-3xl font-bold mb-6">Nasza misja</h2>
              <p className="text-lg text-primary-100 leading-relaxed">
                PulsObywateli powstał z myślą o budowaniu świadomości obywatelskiej 
                i ułatwianiu dostępu do informacji o pracach Sejmu. Chcemy pokazać 
                rzeczywiste nastroje społeczne, niezależnie od sondaży medialnych.
              </p>
            </div>
          </div>

          {/* Funkcjonalności */}
          <div className="mb-16">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white text-center mb-12">
              Co oferujemy
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {features.map((feature, index) => (
                <div key={index} className="text-center">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 dark:bg-primary-900 rounded-full mb-4">
                    <feature.icon className="h-8 w-8 text-primary-600 dark:text-primary-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 text-sm">
                    {feature.description}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Statystyki */}
          <div className="bg-gray-50 dark:bg-gray-800 rounded-2xl p-8 mb-16">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white text-center mb-8">
              Nasze osiągnięcia
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              {stats.map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="text-3xl font-bold text-primary-600 dark:text-primary-400 mb-2">
                    {stat.value}
                  </div>
                  <div className="text-gray-600 dark:text-gray-400">
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Wartości */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
                Nasze wartości
              </h2>
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
                    <ShieldCheckIcon className="h-5 w-5 text-green-600 dark:text-green-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                      Transparentność
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400">
                      Wszystkie dane pochodzą z oficjalnych źródeł. Głosowanie jest anonimowe i bezpieczne.
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                    <GlobeAltIcon className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                      Dostępność
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400">
                      Platforma jest dostępna dla wszystkich obywateli, niezależnie od wieku czy wykształcenia.
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center">
                    <UsersIcon className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                      Społeczność
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400">
                      Budujemy społeczność zaangażowanych obywateli, którzy chcą wpływać na kształt Polski.
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <div>
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
                Jak to działa
              </h2>
              <div className="space-y-4">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
                    <span className="text-sm font-bold text-primary-600 dark:text-primary-400">1</span>
                  </div>
                  <p className="text-gray-600 dark:text-gray-400">
                    Automatycznie pobieramy projekty ustaw z oficjalnych źródeł Sejmu RP
                  </p>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
                    <span className="text-sm font-bold text-primary-600 dark:text-primary-400">2</span>
                  </div>
                  <p className="text-gray-600 dark:text-gray-400">
                    Tworzymy sondaże społeczne na aktualne tematy polityczne i społeczne
                  </p>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
                    <span className="text-sm font-bold text-primary-600 dark:text-primary-400">3</span>
                  </div>
                  <p className="text-gray-600 dark:text-gray-400">
                    Obywatele głosują i wyrażają swoje opinie w bezpiecznym środowisku
                  </p>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
                    <span className="text-sm font-bold text-primary-600 dark:text-primary-400">4</span>
                  </div>
                  <p className="text-gray-600 dark:text-gray-400">
                    Prezentujemy wyniki w przejrzysty sposób, pokazując rzeczywiste nastroje społeczne
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Call to action */}
          <div className="text-center bg-primary-50 dark:bg-primary-900/20 rounded-2xl p-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Dołącz do nas!
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Zarejestruj się i zacznij wpływać na kształt demokracji w Polsce
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="/bills"
                className="btn-primary"
              >
                Przeglądaj projekty ustaw
              </a>
              <a
                href="/polls"
                className="btn-outline"
              >
                Głosuj w sondażach
              </a>
            </div>
          </div>
        </div>
      </Layout>
    </>
  )
}
