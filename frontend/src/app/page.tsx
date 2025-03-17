export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
      <main className="container mx-auto px-4 py-16">
        {/* Hero Section */}
        <section className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-6">
            Explorez les inégalités dans le cinéma
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Découvrez les données et statistiques sur la représentation dans
            l'industrie cinématographique
          </p>
        </section>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          <div className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm">
            <h2 className="text-xl font-bold mb-4">
              Représentation des genres
            </h2>
            <p className="text-gray-600 dark:text-gray-300">
              Analysez la distribution des rôles selon le genre
            </p>
          </div>
          <div className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm">
            <h2 className="text-xl font-bold mb-4">Diversité à l'écran</h2>
            <p className="text-gray-600 dark:text-gray-300">
              Explorez la diversité ethnique et culturelle dans les films
            </p>
          </div>
          <div className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm">
            <h2 className="text-xl font-bold mb-4">Écarts salariaux</h2>
            <p className="text-gray-600 dark:text-gray-300">
              Comparez les rémunérations dans l'industrie
            </p>
          </div>
        </div>

        {/* CTA Section */}
        <section className="text-center">
          <a
            href="/explorer"
            className="inline-block bg-blue-600 text-white px-8 py-3 rounded-full font-medium hover:bg-blue-700 transition-colors"
          >
            Explorer les données
          </a>
        </section>
      </main>
    </div>
  );
}
