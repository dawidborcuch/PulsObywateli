import Link from 'next/link'

export default function Footer() {
  return (
    <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center mb-4">
              <div className="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">P</span>
              </div>
              <div className="ml-3">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                  PulsObywateli
                </h3>
              </div>
            </div>
            <p className="text-gray-600 dark:text-gray-400 text-sm max-w-md">
              Obywatelska platforma sondażowo-informacyjna do śledzenia projektów ustaw 
              i wyrażania opinii na temat polityki w Polsce.
            </p>
          </div>
          
          <div>
            <h4 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider mb-4">
              Platforma
            </h4>
            <ul className="space-y-2">
              <li>
                <Link href="/bills" className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">
                  Projekty ustaw
                </Link>
              </li>
              <li>
                <Link href="/polls" className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">
                  Sondaże
                </Link>
              </li>
              <li>
                <Link href="/ranking" className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">
                  Ranking
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider mb-4">
              Informacje
            </h4>
            <ul className="space-y-2">
              <li>
                <Link href="/about" className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">
                  O projekcie
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">
                  Polityka prywatności
                </Link>
              </li>
              <li>
                <Link href="/terms" className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">
                  Regulamin
                </Link>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="mt-8 pt-8 border-t border-gray-200 dark:border-gray-700">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              © 2024 PulsObywateli. Wszystkie prawa zastrzeżone.
            </p>
            <div className="mt-4 md:mt-0">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Zbudowane z ❤️ dla demokracji
              </p>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}

