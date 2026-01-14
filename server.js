const WebSocket = require('ws');

const PORT = process.env.PORT || 8081;
const wss = new WebSocket.Server({ port: PORT });

// Хранилище: pcName -> {ws, minecraftNick}
const users = new Map();

console.log(`Globals WebSocket Server started on port ${PORT}`);

wss.on('connection', (ws) => {
    console.log('New connection');
    let currentPcName = null;

    ws.on('message', (data) => {
        try {
            const message = JSON.parse(data);
            
            if (message.type === 'register') {
                const pcName = message.pcName;
                const minecraftNick = message.minecraftNick;
                const clientName = message.clientName || 'Unknown';
                const clientVersion = message.clientVersion || '1.0';
                
                console.log('========================================');
                console.log('Received register message:');
                console.log('  Raw message:', JSON.stringify(message));
                console.log('  PC Name:', pcName);
                console.log('  Minecraft Nick:', minecraftNick);
                console.log('  Client Name:', clientName);
                console.log('  Client Version:', clientVersion);
                console.log('========================================');
                
                currentPcName = pcName;
                users.set(pcName, { ws, minecraftNick, clientName, clientVersion });
                
                console.log(`User registered: ${pcName} (${minecraftNick}) - Client: ${clientName} ${clientVersion}`);
                
                // Отправляем список всех пользователей новому клиенту
                const userList = {};
                users.forEach((data, pcName) => {
                    userList[pcName] = {
                        minecraftNick: data.minecraftNick,
                        clientName: data.clientName,
                        clientVersion: data.clientVersion
                    };
                });
                
                ws.send(JSON.stringify({
                    type: 'userlist',
                    users: userList
                }));
                
                // Уведомляем всех остальных о новом пользователе
                broadcast({
                    type: 'user_join',
                    pcName: pcName,
                    minecraftNick: minecraftNick,
                    clientName: clientName,
                    clientVersion: clientVersion
                }, ws);
            }
            else if (message.type === 'snowball_throw') {
                // Ретранслируем снежок всем остальным
                console.log(`Snowball thrown by ${message.pcName}`);
                broadcast(message, ws);
            }
            else if (message.type === 'snowball_hit') {
                // Ретранслируем попадание всем
                console.log(`Snowball hit: ${message.targetNick}`);
                broadcast(message, ws);
            }
            else if (message.type === 'waypoint_place') {
                // Ретранслируем метку всем остальным
                console.log(`Waypoint placed by ${message.pcName} at (${message.px}, ${message.py}, ${message.pz})`);
                broadcast(message, ws);
            }
            else if (message.type === 'waypoint_remove') {
                // Ретранслируем удаление метки всем остальным
                console.log(`Waypoint removed: ${message.id}`);
                broadcast(message, ws);
            }
        } catch (error) {
            console.error('Error parsing message:', error);
        }
    });

    ws.on('close', () => {
        if (currentPcName && users.has(currentPcName)) {
            const userData = users.get(currentPcName);
            console.log(`User disconnected: ${currentPcName} (${userData.minecraftNick})`);
            users.delete(currentPcName);
            
            // Уведомляем всех о выходе пользователя
            broadcast({
                type: 'user_leave',
                pcName: currentPcName
            });
        }
    });

    ws.on('error', (error) => {
        console.error('WebSocket error:', error);
    });
});

function broadcast(message, exclude = null) {
    const messageStr = JSON.stringify(message);
    users.forEach((userData) => {
        if (userData.ws !== exclude && userData.ws.readyState === WebSocket.OPEN) {
            userData.ws.send(messageStr);
        }
    });
}

console.log('Globals Server ready. Waiting for connections...');
