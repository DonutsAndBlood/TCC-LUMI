'use client';

import { websocket } from '@/socketio';
import Image from 'next/image';
import { useEffect, useState } from 'react';
import VLibras from 'vlibras-nextjs';

export default function Home() {
  const [messages, setMessages] = useState([
    {id: 0, text: 'Exemplo de tradução em tempo real'},
    {id: 1, text: 'Esta é uma mensagem de teste.'},
  ]);
  const [isVLibrasReady, setIsVLibrasReady] = useState(false);
  const [currentMessage, setCurrentMessage] = useState(messages[0].id);
  const textContainerSize = 400;
  const maxMessages = 7;

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

  // document.addEventListener('vlibras-ready', () => {

  useEffect(() => {
    websocket.on("transcript",(message: string) => {
      console.log("message", message);
      if (message && message.length > 0) {
        setMessages((prev) => {
          const lastId = prev[prev.length - 1]?.id ?? 0;
          return [...prev, { id: lastId + 1, text: message }]
					// return prev
					// 	.toSpliced(0, 0, { id: lastId + 1, text: message })
					// 	.slice(0, maxMessages);
        });
      }
    });
  }, []);

  // useEffect(() => {
  //   if (!isVLibrasReady || messages.length === 0) return;

  //   if (currentMessage !== messages[messages.length - 1].id) {
  //     const nextMessage = messages[currentMessage + 1];
  //     setCurrentMessage(nextMessage.id);
  //     document.getElementById(`message-${currentMessage}`)?.click();
  //   }
	// 	}, [isVLibrasReady, messages, currentMessage]);

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

      <main className={`w-full max-w-3xl h-[${textContainerSize}] bg-gray-100 dark:bg-zinc-800 rounded-2xl shadow-inner p-4 overflow-y-auto flex flex-col gap-3`}>
        {messages.map((message) => (
          <div
            id={`message-${message.id}`}
            key={message.id}
            className="bg-white dark:bg-zinc-700 text-sm p-3 rounded-lg shadow border border-gray-200 dark:border-zinc-600"
          >
            {message.text}
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
