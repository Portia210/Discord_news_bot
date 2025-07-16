#!/bin/bash

# Configuration
KEY_PAIR="my_key_pair.pem"
USER="ubuntu"
HOST="54.165.14.238"
REMOTE_DIR="~/discord/Discord_news_bot"
VENV_PATH="~/discord/venv"
BOT_NAME="bot.py"
LOCAL_DIR="."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to display menu
show_menu() {
    echo ""
    print_status $BLUE "🤖 Discord Bot Management Script"
    print_status $BLUE "================================"
    echo "1) SSH into server"
    echo "2) Pull nohup.out from server"
    echo "3) Update remote and run bot"
    echo "4) Kill remote bot"
    echo "5) View remote bot status"
    echo "6) Restart EC2 instance"
    echo "7) Exit"
    echo ""
    echo -n "Choose an option (1-7): "
}

# Function to handle SSH connection
ssh_connect() {
    print_status $BLUE "🔗 Connecting with SSH..."
    ssh -i "$KEY_PAIR" "$USER@$HOST"
}

# Function to pull nohup.out
pull_nohup() {
    print_status $BLUE "📥 Copying nohup.out from server to local..."
    scp -i "$KEY_PAIR" "$USER@$HOST":"$REMOTE_DIR/nohup.out" "$LOCAL_DIR"
    if [ $? -eq 0 ]; then
        print_status $GREEN "✅ Successfully copied nohup.out"
    else
        print_status $RED "❌ Failed to copy nohup.out"
    fi
}

# Function to check if bot is running
check_bot_running() {
    ssh -T -i "$KEY_PAIR" "$USER@$HOST" "ps aux | grep -v grep | grep -q bot.py"
    return $?
}

# Function to kill remote bot
kill_bot() {
    print_status $YELLOW "🛑 Killing bot process on remote server..."
    ssh -T -i "$KEY_PAIR" "$USER@$HOST" "pkill -f bot.py"
    if [ $? -eq 0 ]; then
        print_status $GREEN "✅ Bot process killed"
        # Wait a moment for process to fully terminate
        sleep 2
    else
        print_status $YELLOW "⚠️  No bot process found to kill"
    fi
}

# Function to check bot status
check_status() {
    print_status $BLUE "📊 Checking remote bot status..."
    local is_running=$(ssh -T -i "$KEY_PAIR" "$USER@$HOST" "ps aux | grep bot.py | grep -v grep")
    if [ -n "$is_running" ]; then
        print_status $GREEN "✅ Bot is running:"
        echo "$is_running"
        return 0
    else
        print_status $RED "❌ Bot is not running"
        return 1
    fi
}

# Function to wait and verify bot is running
wait_for_bot() {
    print_status $BLUE "⏳ Waiting for bot to start..."
    local attempts=0
    local max_attempts=3
    
    while [ $attempts -lt $max_attempts ]; do
        if check_bot_running; then
            print_status $GREEN "✅ Bot is now running successfully!"
            return 0
        fi
        print_status $YELLOW "⏳ Attempt $((attempts + 1))/$max_attempts - Bot not ready yet..."
        sleep 3
        ((attempts++))
    done
    
    print_status $RED "❌ Bot failed to start after $max_attempts attempts"
    return 1
}

# Function to restart EC2 instance
restart_ec2() {
    print_status $YELLOW "⚠️  WARNING: This will restart the entire EC2 instance!"
    echo -n "Are you sure you want to continue? (y/N): "
    read -r confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        print_status $BLUE "🔄 Restarting EC2 instance..."
        
        # Get instance ID by IP address
        local instance_id=$(aws ec2 describe-instances \
            --filters "Name=ip-address,Values=$HOST" \
            --query "Reservations[*].Instances[*].InstanceId" \
            --output text)
        
        if [ -n "$instance_id" ]; then
            aws ec2 reboot-instances --instance-ids "$instance_id"
            if [ $? -eq 0 ]; then
                print_status $GREEN "✅ EC2 instance restart initiated"
                print_status $BLUE "⏳ Waiting for instance to come back online..."
                
                # Wait for instance to be running again
                local attempts=0
                local max_attempts=20
                while [ $attempts -lt $max_attempts ]; do
                    local status=$(aws ec2 describe-instances \
                        --instance-ids "$instance_id" \
                        --query "Reservations[*].Instances[*].State.Name" \
                        --output text)
                    
                    if [ "$status" = "running" ]; then
                        print_status $GREEN "✅ Instance is back online!"
                        return 0
                    fi
                    
                    print_status $YELLOW "⏳ Instance status: $status (attempt $((attempts + 1))/$max_attempts)"
                    sleep 10
                    ((attempts++))
                done
                
                print_status $RED "❌ Instance took too long to restart"
            else
                print_status $RED "❌ Failed to restart EC2 instance"
            fi
        else
            print_status $RED "❌ Could not find EC2 instance with IP $HOST"
        fi
    else
        print_status $BLUE "🛑 Restart cancelled"
    fi
}

# Function to update and run bot
update_and_run() {
    print_status $BLUE "🔄 Updating EC2..."
    
    # Update code and dependencies
    ssh -T -i "$KEY_PAIR" "$USER@$HOST" << EOF
        cd $REMOTE_DIR
        git checkout master
        git pull origin master
        source $VENV_PATH/bin/activate
        pip install -r requirements.txt > /dev/null 2>&1
EOF
    
    if [ $? -eq 0 ]; then
        print_status $GREEN "✅ Update completed"
    else
        print_status $RED "❌ Update failed"
        return 1
    fi

    # Kill existing bot if running
    if check_bot_running; then
        kill_bot
    fi

    # Start the bot
    print_status $BLUE "🚀 Starting bot..."
    ssh -T -i "$KEY_PAIR" "$USER@$HOST" << EOF
        cd $REMOTE_DIR
        rm -f nohup.out
        source $VENV_PATH/bin/activate
        nohup python bot.py > nohup.out 2>&1 &
EOF

    if [ $? -eq 0 ]; then
        print_status $GREEN "✅ Bot start command executed"
        # Wait and verify bot is actually running
        wait_for_bot
    else
        print_status $RED "❌ Failed to start bot"
        return 1
    fi
}

# Main interactive loop
main() {
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
                restart_ec2
                ;;
            7)
                print_status $GREEN "👋 Goodbye!"
            exit 0
            ;;
        *)
                print_status $RED "❌ Invalid option. Please choose 1-7."
            ;;
    esac
    
    echo ""
    echo "Press Enter to continue..."
    read -r
done
}

# Run main function
main
