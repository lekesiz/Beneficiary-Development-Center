import React, { useState, useEffect } from 'react';
import { useSocket } from '@/contexts/SocketContext';
import { useAuth } from '@/contexts/AuthContext';
import { Wifi, WifiOff, Send, Activity, Users, MessageSquare } from 'lucide-react';

export default function TestRealtime() {
  const { socket, isConnected } = useSocket();
  const { user } = useAuth();
  const [logs, setLogs] = useState<string[]>([]);
  const [message, setMessage] = useState('');
  const [room, setRoom] = useState('test-room');
  const [onlineUsers, setOnlineUsers] = useState<string[]>([]);

  const addLog = (message: string, type: 'info' | 'success' | 'error' | 'received' = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    const prefix = 
      type === 'success' ? '✅' : 
      type === 'error' ? '❌' : 
      type === 'received' ? '📥' :
      '📤';
    setLogs(prev => [...prev, `[${timestamp}] ${prefix} ${message}`]);
  };

  useEffect(() => {
    if (!socket) {
      addLog('Socket not initialized', 'error');
      return;
    }

    // Socket event listeners
    socket.on('connect', () => {
      addLog('Connected to server', 'success');
      socket.emit('join_room', { room });
    });

    socket.on('disconnect', () => {
      addLog('Disconnected from server', 'error');
    });

    socket.on('message', (data: any) => {
      addLog(`Message from ${data.user}: ${data.message}`, 'received');
    });

    socket.on('user_joined', (data: any) => {
      addLog(`${data.user} joined the room`, 'info');
      if (data.users) {
        setOnlineUsers(data.users);
      }
    });

    socket.on('user_left', (data: any) => {
      addLog(`${data.user} left the room`, 'info');
      if (data.users) {
        setOnlineUsers(data.users);
      }
    });

    socket.on('notification', (data: any) => {
      addLog(`Notification: ${data.type} - ${data.message}`, 'received');
    });

    socket.on('error', (error: any) => {
      addLog(`Socket error: ${error.message || error}`, 'error');
    });

    // Join room on mount
    if (isConnected) {
      socket.emit('join_room', { room });
      addLog(`Joining room: ${room}`, 'info');
    }

    return () => {
      socket.off('connect');
      socket.off('disconnect');
      socket.off('message');
      socket.off('user_joined');
      socket.off('user_left');
      socket.off('notification');
      socket.off('error');
      
      if (isConnected) {
        socket.emit('leave_room', { room });
      }
    };
  }, [socket, isConnected, room]);

  const sendMessage = () => {
    if (!socket || !isConnected || !message.trim()) return;

    socket.emit('send_message', {
      room,
      message: message.trim(),
      user: user?.email || 'Anonymous',
    });

    addLog(`Sent: ${message}`, 'success');
    setMessage('');
  };

  const joinRoom = (newRoom: string) => {
    if (!socket || !isConnected) return;

    // Leave current room
    socket.emit('leave_room', { room });
    addLog(`Left room: ${room}`, 'info');

    // Join new room
    setRoom(newRoom);
    socket.emit('join_room', { room: newRoom });
    addLog(`Joined room: ${newRoom}`, 'success');
  };

  const testNotification = () => {
    if (!socket || !isConnected) return;

    socket.emit('test_notification', {
      type: 'info',
      message: 'This is a test notification',
      user: user?.email,
    });

    addLog('Sent test notification', 'info');
  };

  const clearLogs = () => {
    setLogs([]);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Real-time Features Test</h1>

        {/* Connection Status */}
        <div className="bg-white p-4 rounded-lg shadow mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              {isConnected ? (
                <>
                  <Wifi className="h-6 w-6 text-green-600 mr-3" />
                  <span className="text-green-600 font-medium">Connected</span>
                </>
              ) : (
                <>
                  <WifiOff className="h-6 w-6 text-red-600 mr-3" />
                  <span className="text-red-600 font-medium">Disconnected</span>
                </>
              )}
            </div>
            <div className="flex items-center text-sm text-gray-600">
              <Users className="h-4 w-4 mr-2" />
              <span>{onlineUsers.length} users online</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Controls */}
          <div className="lg:col-span-1 space-y-6">
            {/* Room Selection */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Rooms</h2>
              <div className="space-y-2">
                {['test-room', 'general', 'admin-room', 'trainer-room'].map((roomName) => (
                  <button
                    key={roomName}
                    onClick={() => joinRoom(roomName)}
                    className={`w-full px-4 py-2 rounded text-left ${
                      room === roomName
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 hover:bg-gray-200'
                    }`}
                  >
                    {roomName}
                  </button>
                ))}
              </div>
              <p className="text-sm text-gray-600 mt-3">
                Current room: <span className="font-medium">{room}</span>
              </p>
            </div>

            {/* Test Actions */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Test Actions</h2>
              <div className="space-y-3">
                <button
                  onClick={testNotification}
                  disabled={!isConnected}
                  className="w-full px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded disabled:bg-gray-400"
                >
                  Send Test Notification
                </button>
                <button
                  onClick={clearLogs}
                  className="w-full px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded"
                >
                  Clear Logs
                </button>
              </div>
            </div>
          </div>

          {/* Chat Interface */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow h-full flex flex-col">
              {/* Header */}
              <div className="p-4 border-b">
                <div className="flex items-center">
                  <MessageSquare className="h-5 w-5 mr-2 text-gray-600" />
                  <h2 className="text-xl font-semibold">Real-time Chat</h2>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 p-4 overflow-y-auto bg-gray-50">
                <div className="space-y-2 font-mono text-sm">
                  {logs.length > 0 ? (
                    logs.map((log, index) => (
                      <div
                        key={index}
                        className={`p-2 rounded ${
                          log.includes('📥') ? 'bg-blue-100' :
                          log.includes('✅') ? 'bg-green-100' :
                          log.includes('❌') ? 'bg-red-100' :
                          'bg-white'
                        }`}
                      >
                        {log}
                      </div>
                    ))
                  ) : (
                    <div className="text-gray-500 text-center">
                      No messages yet. Try sending a message or joining a room.
                    </div>
                  )}
                </div>
              </div>

              {/* Input */}
              <div className="p-4 border-t">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Type a message..."
                    disabled={!isConnected}
                    className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!isConnected || !message.trim()}
                    className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:bg-gray-400 flex items-center"
                  >
                    <Send className="h-4 w-4 mr-2" />
                    Send
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Info Panel */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex">
            <Activity className="h-5 w-5 text-blue-600 mr-3 flex-shrink-0" />
            <div>
              <h3 className="font-semibold text-blue-900">Socket.IO Test</h3>
              <p className="text-sm text-blue-800 mt-1">
                This page tests real-time communication features. Messages sent here will be broadcast
                to all users in the same room. Try opening this page in multiple browser tabs to see
                real-time updates.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}