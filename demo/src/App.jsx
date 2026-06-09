import Header from './components/Header';
import ChatPanel from './components/ChatPanel';

export default function App() {
  return (
    <div className="h-screen flex flex-col bg-slate-900">
      <ChatPanel />
    </div>
  );
}
