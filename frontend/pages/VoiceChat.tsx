import React, { useState } from "react";
import MicRecorder from "../components/MicRecorder";
import VoiceBall from "../components/VoiceBall";
import "../styles/mic-recorder.css";

const VoiceChat: React.FC = () => {
  const [emotionTags, setEmotionTags] = useState<string[]>([]);
  const [isSpeaking, setIsSpeaking] = useState(false);

  return (
    <div className="voice-chat-container">
      <header className="voice-chat-header">
        <h1>🌸 花小軟語魂實境</h1>
        <p>按下錄音開始說話，小軟會即時聆聽並回應你。</p>
      </header>

      <div className="voiceball-section">
        <VoiceBall tags={emotionTags} isActive={isSpeaking} />
        <p className="voiceball-caption">
          {emotionTags.length > 0
            ? `感知情緒：${emotionTags.join("、")}`
            : "等待語氣訊號..."}
        </p>
      </div>

      <main className="voice-chat-main">
        <section className="voice-chat-transcript">
          <h2>即時字幕</h2>
          <MicRecorder onVoiceTagsChange={setEmotionTags} onSpeakingChange={setIsSpeaking} />
        </section>

        <aside className="voice-chat-help">
          <h3>操作提示</h3>
          <ul>
            <li>點擊「開始錄音」允許麥克風權限</li>
            <li>錄音時保持穩定語速，系統會自動斷句</li>
            <li>若出現錯誤，可重新整理或檢查 API key</li>
          </ul>
        </aside>
      </main>
    </div>
  );
};

export default VoiceChat;

