#!/bin/bash

# Configuration
KEY_PAIR="my_key_pair.pem"
USER="ubuntu"
HOST="54.165.14.238"
REMOTE_VENV_DIR="~/discord/venv"
REMOTE_MAIN_DIR="~/discord/Discord_news_bot"
REMOTE_BOT_DIR="~/discord/Discord_news_bot/bot"
REMOTE_WEBSITE_DIR="~/discord/Discord_news_bot/website"
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
    echo "2) Pull bot nohup.out from server"
    echo "3) Pull website nohup.out from server"
    echo "4) Copy .env file to server"
    echo "5) Update remote and run bot"
    echo "6) Update remote and run server"
    echo "7) Update remote and run all"
    echo "8) Kill remote bot"
    echo "9) Kill remote server"
    echo "10) View remote bot status"
    echo "11) View remote server status"
    echo "12) Restart EC2 instance"
    echo "13) Exit"
    echo ""
    echo -n "Choose an option (1-12): "
}

# Function to handle SSH connection
ssh_connect() {
    print_status $BLUE "🔗 Connecting with SSH..."
    ssh -i "$KEY_PAIR" "$USER@$HOST"
}

# Function to pull nohup.out
pull_bot_nohup() {
    print_status $BLUE "📥 Copying nohup.out from server to local..."
    scp -i "$KEY_PAIR" "$USER@$HOST":"$REMOTE_BOT_DIR/bot_nohup.out" "$LOCAL_DIR"
    if [ $? -eq 0 ]; then
        print_status $GREEN "✅ Successfully copied bot_nohup.out"
    else
        print_status $RED "❌ Failed to copy bot_nohup.out"
    fi
}

# Function to pull website nohup.out
pull_website_nohup() {
    print_status $BLUE "📥 Copying nohup_website.out from server to local..."
    scp -i "$KEY_PAIR" "$USER@$HOST":"$REMOTE_WEBSITE_DIR/nohup_website.out" "$LOCAL_DIR"
    if [ $? -eq 0 ]; then
        print_status $GREEN "✅ Successfully copied nohup_website.out"
    else
        print_status $RED "❌ Failed to copy nohup_website.out"
    fi
}

copy_env_file_to_server() {
    print_status $BLUE "📥 Copying .env file to server..."
    scp -i "$KEY_PAIR" "$LOCAL_DIR/.env" "$USER@$HOST":"$REMOTE_MAIN_DIR"
    if [ $? -eq 0 ]; then
        print_status $GREEN "✅ Successfully copied .env file to bot directory"
    else
        print_status $RED "❌ Failed to copy .env file"
    fi
}

# Generic function to check if a process is running
check_process_running() {
    local process_name=$1
    ssh -T -i "$KEY_PAIR" "$USER@$HOST" "ps aux | grep -v grep | grep -q $process_name"
    return $?
}

# Generic function to kill a process
kill_process() {
    local process_name=$1
    local display_name=$2
    print_status $YELLOW "🛑 Killing $display_name process on remote server..."
    ssh -T -i "$KEY_PAIR" "$USER@$HOST" "pkill -f $process_name"
    if [ $? -eq 0 ]; then
        print_status $GREEN "✅ $display_name process killed"
        # Wait a moment for process to fully terminate
        sleep 2
    else
        print_status $YELLOW "⚠️  No $display_name process found to kill"
    fi
}

# Generic function to check process status
check_status() {
    local process_name=$1
    local display_name=$2
    print_status $BLUE "📊 Checking remote $display_name status..."
    local is_running=$(ssh -T -i "$KEY_PAIR" "$USER@$HOST" "ps aux | grep $process_name | grep -v grep")
    if [ -n "$is_running" ]; then
        print_status $GREEN "✅ $display_name is running:"
        echo "$is_running"
        return 0
    else
        print_status $RED "❌ $display_name is not running"
        return 1
    fi
}

# Generic function to wait and verify process is running
wait_for_process() {
    local process_name=$1
    local display_name=$2
    print_status $BLUE "⏳ Waiting for $display_name to start..."
    local attempts=0
    local max_attempts=3
    
    while [ $attempts -lt $max_attempts ]; do
        if check_process_running "$process_name"; then
            print_status $GREEN "✅ $display_name is now running successfully!"
            return 0
        fi
        print_status $YELLOW "⏳ Attempt $((attempts + 1))/$max_attempts - $display_name not ready yet..."
        sleep 3
        ((attempts++))
    done
    
    print_status $RED "❌ $display_name failed to start after $max_attempts attempts"
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

update_project() {
    print_status $BLUE "🔄 Updating EC2..."
    
    # Update code and dependencies
    ssh -T -i "$KEY_PAIR" "$USER@$HOST" << EOF
        cd $REMOTE_MAIN_DIR
        git stash
        git checkout master
        
        # Clean up untracked files that might conflict with pull
        git clean -fd
        
        git pull origin master
        source $VENV_PATH/bin/activate
        
        # Install bot requirements
        cd $REMOTE_BOT_DIR
        pip install -r requirements.txt > /dev/null 2>&1
        
        # Install website requirements
        cd $REMOTE_WEBSITE_DIR
        pip install -r requirements.txt > /dev/null 2>&1
EOF
    
    if [ $? -eq 0 ]; then
        print_status $GREEN "✅ Update completed"
    else
        print_status $RED "❌ Update failed"
        return 1
    fi
}

# Generic function to update and run a process
update_and_run_process() {
    local process_name=$1
    local display_name=$2
    local start_command=$3
    local log_file=$4
    local working_dir=$5
    
    update_project
    if [ $? -ne 0 ]; then
        return 1
    fi

    # Kill existing process if running
    if check_process_running "$process_name"; then
        kill_process "$process_name" "$display_name"
    fi

    # Start the process
    print_status $BLUE "🚀 Starting $display_name..."
    ssh -T -i "$KEY_PAIR" "$USER@$HOST" << EOF
        cd $working_dir
        source $VENV_PATH/bin/activate
        rm -f $log_file
        $start_command
EOF

    if [ $? -eq 0 ]; then
        print_status $GREEN "✅ $display_name start command executed"
        # Wait and verify process is actually running
        wait_for_process "$process_name" "$display_name"
    else
        print_status $RED "❌ Failed to start $display_name"
        return 1
    fi
}

# Function to update and run bot
update_and_run_bot() {
    update_and_run_process \
        "bot.py" \
        "bot" \
        "nohup python bot.py > bot_nohup.out 2>&1 &" \
        "bot_nohup.out" \
        "$REMOTE_BOT_DIR"
}

# Function to update and run server
update_and_run_server() {
    update_and_run_process \
        "gunicorn" \
        "server" \
        "nohup gunicorn server:app --bind 0.0.0.0:8000 --workers 2 --timeout 120 --keep-alive 5 --max-requests 1000 --max-requests-jitter 100 --access-logfile - --error-logfile - --log-level info > nohup_website.out 2>&1 &" \
        "nohup_website.out" \
        "$REMOTE_WEBSITE_DIR"
}

update_and_run_all() {
    update_and_run_server
    update_and_run_bot
}

# Function to kill bot (using generic function)
kill_bot() {
    kill_process "bot.py" "bot"
}

# Function to kill server (using generic function)
kill_server() {
    kill_process "gunicorn" "server"
}

# Function to check bot status (using generic function)
check_bot_status() {
    check_status "bot.py" "bot"
}

# Function to check server status (using generic function)
check_server_status() {
    check_status "gunicorn" "server"
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
            pull_bot_nohup
            ;;
        3)
            pull_website_nohup
            ;;
        4)
            copy_env_file_to_server
            ;;
        5)
            update_and_run_bot
            ;;
        6)
            update_and_run_server
            ;;
        7)
            update_and_run_all
            ;;
        8)
            kill_bot
            ;;
        9)
            kill_server
            ;;
        10)
            check_bot_status
            ;;  
        11)
            check_server_status
            ;;
        12)
            restart_ec2
            ;;
        13)
            print_status $GREEN "👋 Goodbye!"
            exit 0
            ;;
        *)
            print_status $RED "❌ Invalid option. Please choose 1-13."
            ;;
    esac
    
    echo ""
    echo "Press Enter to continue..."
    read -r
done
}

# Run main function
main
