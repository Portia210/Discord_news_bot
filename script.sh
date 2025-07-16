#!/bin/bash

# Vars
KEY_PAIR="my_key_pair.pem"
USER="ubuntu"
HOST="54.165.14.238"
REMOTE_DIR="~/discord/stock-news-bot"
BOT_NAME="bot.py"
LOCAL_DIR="."

# Function to display menu
show_menu() {
    echo ""
    echo "🤖 Discord Bot Management Script"
    echo "================================"
    echo "1) SSH into server"
    echo "2) Pull nohup.out from server"
    echo "3) Update remote and run bot"
    echo "4) Kill remote bot"
    echo "5) View remote bot status"
    echo "6) Exit"
    echo ""
    echo -n "Choose an option (1-6): "
}

# Function to handle SSH connection
ssh_connect() {
    echo "🔗 Connecting with SSH..."
    ssh -i "$KEY_PAIR" "$USER@$HOST"
}

# Function to pull nohup.out
pull_nohup() {
    echo "📥 Copying nohup.out from server to local..."
    scp -i "$KEY_PAIR" "$USER@$HOST":"$REMOTE_DIR/nohup.out" "$LOCAL_DIR"
    if [ $? -eq 0 ]; then
        echo "✅ Successfully copied nohup.out"
    else
        echo "❌ Failed to copy nohup.out"
    fi
}



# Function to update and run bot (Alternative multi-line approach)
update_and_run() {
    echo "🔄 Updating EC2..."
    
    # Method 3: Here Document (multi-line SSH)
    ssh -i "$KEY_PAIR" "$USER@$HOST" << 'EOF'
        cd ~/discord/stock-news-bot
        source venv/bin/activate
        git pull
        pip install -r requirements.txt
EOF
    
    if [ $? -eq 0 ]; then
        echo "✅ Update completed"
    else
        echo "❌ Update failed"
        return 1
    fi

    # check if bot is running
    if check_status; then
        kill_bot
    fi

    # remove nohup.out if exists on remote server
    echo "🗑️ Removing old nohup.out and running bot..."
    ssh -i "$KEY_PAIR" "$USER@$HOST" << 'EOF'
        cd ~/discord/stock-news-bot
        rm -f nohup.out
        source venv/bin/activate
        nohup python bot.py > nohup.out 2>&1 &
EOF

    if [ $? -eq 0 ]; then
        echo "✅ Bot started successfully"
    else
        echo "❌ Failed to start bot"
    fi
}

# Function to kill remote bot
kill_bot() {
    echo "🛑 Killing bot process on remote server..."
    ssh -i "$KEY_PAIR" "$USER@$HOST" "pkill -f bot.py"
    if [ $? -eq 0 ]; then
        echo "✅ Bot process killed"
    else
        echo "❌ Failed to kill bot process (might not be running)"
    fi
}

# Function to check bot status
check_status() {
    echo "📊 Checking remote bot status..."
    ssh -i "$KEY_PAIR" "$USER@$HOST" "ps aux | grep bot.py | grep -v grep"
    if [ $? -eq 0 ]; then
        return 0
    else
        return 1
    fi
}


# Main interactive loop
while true; do
    show_menu
    read -r choice
    
    case $choice in
        1)
            ssh_connect
            ;;
        2)
            pull_nohup
            ;;
        3)
            update_and_run
            ;;
        4)
            kill_bot
            ;;
        5)
            check_status
            ;;
        6)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Please choose 1-7."
            ;;
    esac
    
    echo ""
    echo "Press Enter to continue..."
    read -r
done
