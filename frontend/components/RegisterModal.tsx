import { useState } from 'react'
import { Dialog } from '@headlessui/react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { useAuth } from '@/contexts/AuthContext'
import { useForm } from 'react-hook-form'

interface RegisterModalProps {
  open: boolean
  setOpen: (open: boolean) => void
}

interface RegisterFormData {
  email: string
  username: string
  nickname: string
  password: string
  password_confirm: string
  first_name?: string
  last_name?: string
}

export default function RegisterModal({ open, setOpen }: RegisterModalProps) {
  const [loading, setLoading] = useState(false)
  const { register: registerUser } = useAuth()
  const { register, handleSubmit, formState: { errors }, watch } = useForm<RegisterFormData>()

  const password = watch('password')

  const onSubmit = async (data: RegisterFormData) => {
    setLoading(true)
    try {
      await registerUser(data)
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
        <Dialog.Panel className="mx-auto max-w-md w-full bg-white dark:bg-gray-800 rounded-lg shadow-xl">
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <Dialog.Title className="text-lg font-semibold text-gray-900 dark:text-white">
              Zarejestruj się
            </Dialog.Title>
            <button
              onClick={() => setOpen(false)}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>
          
          <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="first_name" className="label">
                  Imię
                </label>
                <input
                  {...register('first_name')}
                  type="text"
                  id="first_name"
                  className="input"
                  placeholder="Jan"
                />
              </div>
              
              <div>
                <label htmlFor="last_name" className="label">
                  Nazwisko
                </label>
                <input
                  {...register('last_name')}
                  type="text"
                  id="last_name"
                  className="input"
                  placeholder="Kowalski"
                />
              </div>
            </div>
            
            <div>
              <label htmlFor="email" className="label">
                Adres email *
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
              <label htmlFor="username" className="label">
                Nazwa użytkownika *
              </label>
              <input
                {...register('username', { 
                  required: 'Nazwa użytkownika jest wymagana',
                  minLength: {
                    value: 3,
                    message: 'Nazwa użytkownika musi mieć co najmniej 3 znaki'
                  }
                })}
                type="text"
                id="username"
                className="input"
                placeholder="jan_kowalski"
              />
              {errors.username && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {errors.username.message}
                </p>
              )}
            </div>
            
            <div>
              <label htmlFor="nickname" className="label">
                Pseudonim publiczny *
              </label>
              <input
                {...register('nickname', { 
                  required: 'Pseudonim jest wymagany',
                  minLength: {
                    value: 2,
                    message: 'Pseudonim musi mieć co najmniej 2 znaki'
                  }
                })}
                type="text"
                id="nickname"
                className="input"
                placeholder="Jan K."
              />
              {errors.nickname && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {errors.nickname.message}
                </p>
              )}
            </div>
            
            <div>
              <label htmlFor="password" className="label">
                Hasło *
              </label>
              <input
                {...register('password', { 
                  required: 'Hasło jest wymagane',
                  minLength: {
                    value: 8,
                    message: 'Hasło musi mieć co najmniej 8 znaków'
                  }
                })}
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
            
            <div>
              <label htmlFor="password_confirm" className="label">
                Potwierdź hasło *
              </label>
              <input
                {...register('password_confirm', { 
                  required: 'Potwierdzenie hasła jest wymagane',
                  validate: value => value === password || 'Hasła nie są identyczne'
                })}
                type="password"
                id="password_confirm"
                className="input"
                placeholder="••••••••"
              />
              {errors.password_confirm && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {errors.password_confirm.message}
                </p>
              )}
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Rejestracja...' : 'Zarejestruj się'}
            </button>
          </form>
        </Dialog.Panel>
      </div>
    </Dialog>
  )
}

