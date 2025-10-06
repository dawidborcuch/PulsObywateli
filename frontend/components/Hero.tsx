import Link from 'next/link'
import { useAuth } from '@/contexts/AuthContext'

export default function Hero() {
  const { user } = useAuth()

  return (
    <div className="bg-gradient-to-r from-primary-600 to-primary-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
            PulsObywateli
          </h1>
          <p className="text-xl md:text-2xl text-primary-100 mb-8 max-w-3xl mx-auto">
            Obywatelska platforma sondażowo-informacyjna do śledzenia projektów ustaw 
            i wyrażania opinii na temat polityki w Polsce
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/bills"
              className="bg-white text-primary-600 hover:bg-primary-50 font-semibold py-3 px-8 rounded-lg transition-colors duration-200"
            >
              Przeglądaj projekty ustaw
            </Link>
            <Link
              href="/polls"
              className="border-2 border-white text-white hover:bg-white hover:text-primary-600 font-semibold py-3 px-8 rounded-lg transition-colors duration-200"
            >
              Głosuj w sondażach
            </Link>
          </div>
          
          {!user && (
            <p className="mt-8 text-primary-100">
              <Link href="/register" className="underline hover:text-white">
                Zarejestruj się
              </Link>
              {' '}aby móc głosować i komentować
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

