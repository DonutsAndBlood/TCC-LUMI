'use client';
import { useEffect, useState } from 'react';
import VLibras from 'vlibras-nextjs';
import Image from 'next/image';

export default function Home() {
  const [messages, setMessages] = useState([
    'Exemplo de tradução em tempo real',
    'Esta é uma mensagem de teste.',
    'Aprenda libras!',
  ]);

  //useEffect para clicar no botão de acesso do VLibras assim que abre a página
  useEffect(() => {
    const interval = setInterval(() => {
      const accessBtn = document.querySelector('[vw-access-button]');
      if (accessBtn) {
        (accessBtn as HTMLElement).click();
        clearInterval(interval);
      }
    }, 500);
    return () => clearInterval(interval);
  }, []);

  //eu não sei se isso ataliza o useState de mensagens
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8765');//acho que o endereço é esse

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.message) {
        setMessages((prev) => [...prev, data.message]);
      }
    };

    return () => ws.close();
  }, []);

  return (
    <div className="min-h-screen bg-white dark:bg-zinc-900 text-black dark:text-white flex flex-col items-center p-6 sm:p-10 gap-10">
      <header className="flex flex-col items-center gap-4">
        <div className="w-32 h-32 rounded-full overflow-hidden border-4 border-white shadow-lg">
          <Image
            src="/bot-icon.png"
            alt="Avatar do Bot"
            width={128}
            height={128}
            className="object-cover w-full h-full"
          />
        </div>

        <h1 className="text-3xl sm:text-4xl font-bold text-center">
          Lumi
        </h1>
        <p className="text-center max-w-2xl text-sm sm:text-base text-gray-600 dark:text-gray-300">
          As mensagens de voz serão convertidas para texto e exibidas abaixo em
          tempo real. O VLibras será responsável por traduzi-las automaticamente para Libras.
        </p>
      </header>

      <main className="w-full max-w-3xl h-[400px] bg-gray-100 dark:bg-zinc-800 rounded-2xl shadow-inner p-4 overflow-y-auto flex flex-col gap-3">
        {messages.map((msg, index) => (
          <div
            key={index}
            className="bg-white dark:bg-zinc-700 text-sm p-3 rounded-lg shadow border border-gray-200 dark:border-zinc-600"
          >
            {msg}
          </div>
        ))}
      </main>

      <footer className="text-xs text-gray-400 dark:text-gray-500 mt-auto">
        Desenvolvido por Brayan Bautz e Henrique Klayton • Projeto com VLibras
      </footer>

      <VLibras forceOnload />
    </div>
  );
}
