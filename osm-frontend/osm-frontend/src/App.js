// src/App.js
import React from 'react';
import MapInterface from './components/MapInterface';
import './App.css';

function App() {
  return (
    <div className="App">
      <header>
        <h1>OSM Mapping Application</h1>
      </header>
      <main>
        <MapInterface />
      </main>
    </div>
  );
}

export default App;
