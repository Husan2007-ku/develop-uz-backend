import Link from 'next/link'

export default function DashboardPage() {
  const stats = [
    { icon: '🔥', label: 'Streak', value: '0 kun', color: 'text-orange-400' },
    { icon: '⭐', label: 'XP ball', value: '0', color: 'text-yellow-400' },
    { icon: '🧠', label: 'Yodlangan', value: '0 so\'z', color: 'text-blue-400' },
    { icon: '📝', label: 'O\'qilgan', value: '0 essay', color: 'text-green-400' },
  ]

  const quickLinks = [
    { icon: '📝', title: 'Essay o\'qi', desc: '1000+ Writing essay', href: '/essays', color: 'border-blue-500/30' },
    { icon: '🧠', title: 'Vocabulary', desc: '10,000+ so\'z', href: '/vocabulary', color: 'border-purple-500/30' },
    { icon: '✍️', title: 'Study Zone', desc: 'Flashcard va testlar', href: '/study', color: 'border-green-500/30' },
    { icon: '📱', title: 'Telegram Bot', desc: 'Botda davom et', href: 'https://t.me/your_bot_username', color: 'border-orange-500/30' },
  ]

  return (
    <main className="min-h-screen bg-gray-950 text-white">
      <div className="bg-gray-900 border-b border-white/10">
        <div className="max-w-6xl mx-auto px-6 py-10">
          <h1 className="text-4xl font-black mb-2">📊 Dashboard</h1>
          <p className="text-gray-400">
            Progressingizni kuzating va o'rganishni davom eting
          </p>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-10">

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
          {stats.map((s, i) => (
            <div key={i}
              className="bg-white/5 border border-white/10 rounded-2xl p-6 text-center">
              <div className="text-3xl mb-2">{s.icon}</div>
              <div className={`text-2xl font-black mb-1 ${s.color}`}>
                {s.value}
              </div>
              <div className="text-gray-400 text-sm">{s.label}</div>
            </div>
          ))}
        </div>

        {/* Telegram notice */}
        <div className="bg-blue-500/10 border border-blue-500/20 rounded-2xl p-6 mb-10">
          <div className="flex items-center gap-3 mb-2">
            <span className="text-2xl">📱</span>
            <h3 className="font-bold text-lg">Telegram bot orqali kirish</h3>
          </div>
          <p className="text-gray-400 text-sm mb-4">
            To'liq progress, streak va XP ballarni ko'rish uchun
            Telegram botimizga kiring. Barcha ma'lumotlar bot orqali saqlanadi.
          </p>
          <Link href="https://t.me/your_bot_username" target="_blank"
            className="inline-block px-5 py-2.5 bg-blue-600 hover:bg-blue-500 rounded-xl text-sm font-bold text-white transition">
            📱 Botga o'tish →
          </Link>
        </div>

        {/* Quick links */}
        <h2 className="text-xl font-black mb-5">🚀 Tezkor kirish</h2>
        <div className="grid md:grid-cols-2 gap-4">
          {quickLinks.map((l, i) => (
            <Link key={i} href={l.href}
              className={`bg-white/5 border ${l.color} rounded-2xl p-5 flex items-center gap-4 hover:bg-white/10 transition`}>
              <span className="text-3xl">{l.icon}</span>
              <div>
                <div className="font-bold">{l.title}</div>
                <div className="text-gray-400 text-sm">{l.desc}</div>
              </div>
              <span className="ml-auto text-gray-500">→</span>
            </Link>
          ))}
        </div>

      </div>
    </main>
  )
}
