import { useState } from 'react'
import { Dialog } from '@headlessui/react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { useAuth } from '@/contexts/AuthContext'
import { useForm } from 'react-hook-form'

interface LoginModalProps {
  open: boolean
  setOpen: (open: boolean) => void
}

interface LoginFormData {
  email: string
  password: string
}

export default function LoginModal({ open, setOpen }: LoginModalProps) {
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>()

  const onSubmit = async (data: LoginFormData) => {
    setLoading(true)
    try {
      await login(data.email, data.password)
      setOpen(false)
    } catch (error) {
      // Error handling is done in AuthContext
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={setOpen} className="relative z-50">
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
      
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="mx-auto max-w-sm w-full bg-white dark:bg-gray-800 rounded-lg shadow-xl">
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <Dialog.Title className="text-lg font-semibold text-gray-900 dark:text-white">
              Zaloguj się
            </Dialog.Title>
            <button
              onClick={() => setOpen(false)}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>
          
          <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
            <div>
              <label htmlFor="email" className="label">
                Adres email
              </label>
              <input
                {...register('email', { 
                  required: 'Email jest wymagany',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Nieprawidłowy format email'
                  }
                })}
                type="email"
                id="email"
                className="input"
                placeholder="twoj@email.pl"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {errors.email.message}
                </p>
              )}
            </div>
            
            <div>
              <label htmlFor="password" className="label">
                Hasło
              </label>
              <input
                {...register('password', { required: 'Hasło jest wymagane' })}
                type="password"
                id="password"
                className="input"
                placeholder="••••••••"
              />
              {errors.password && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {errors.password.message}
                </p>
              )}
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Logowanie...' : 'Zaloguj się'}
            </button>
          </form>
        </Dialog.Panel>
      </div>
    </Dialog>
  )
}

