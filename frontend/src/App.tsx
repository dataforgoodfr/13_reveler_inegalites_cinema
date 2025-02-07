import './App.css'

function App() {
  return (
    <>
      <div className='flex justify-evenly'>
        <a href="https://collectif5050.com">
          <img src="https://collectif5050.com/wordpress/wp-content/uploads/2022/02/logo_white.svg" className="logo" alt='Collectif 50/50 logo'/>
        </a>
        <a href="https://dataforgood.fr/">
          <img src="https://dataforgood.fr/img/logo-dfg-new2.png" className="logo" alt="Data for Good logo" />
        </a>
      </div>
      <h1>Collectif 50/50 + Data For Good</h1>
      <div className="card">
        <p>
          Edit <code>src/App.tsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Collectif 50/50 and Data For Good logos to learn more
      </p>
    </>
  )
}

export default App
