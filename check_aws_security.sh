#!/bin/bash

# Configuration
KEY_PAIR="my_key_pair.pem"
USER="ubuntu"
HOST="54.165.14.238"

echo "🔍 Checking AWS Security Group Configuration..."

# Get instance ID from IP
echo "1. Finding EC2 instance ID..."
INSTANCE_ID=$(aws ec2 describe-instances \
    --filters "Name=ip-address,Values=$HOST" \
    --query "Reservations[*].Instances[*].InstanceId" \
    --output text)

if [ -n "$INSTANCE_ID" ]; then
    echo "✅ Found instance: $INSTANCE_ID"
else
    echo "❌ Could not find instance with IP $HOST"
    exit 1
fi

# Get security group ID
echo ""
echo "2. Getting security group ID..."
SG_ID=$(aws ec2 describe-instances \
    --instance-ids "$INSTANCE_ID" \
    --query "Reservations[*].Instances[*].SecurityGroups[*].GroupId" \
    --output text)

if [ -n "$SG_ID" ]; then
    echo "✅ Security Group: $SG_ID"
else
    echo "❌ Could not find security group"
    exit 1
fi

# Check current inbound rules
echo ""
echo "3. Current inbound rules:"
aws ec2 describe-security-groups \
    --group-ids "$SG_ID" \
    --query "SecurityGroups[*].IpPermissions[*].[FromPort,ToPort,IpProtocol,IpRanges[*].CidrIp]" \
    --output table

# Check if port 8000 is open
echo ""
echo "4. Checking if port 8000 is allowed..."
PORT_8000_OPEN=$(aws ec2 describe-security-groups \
    --group-ids "$SG_ID" \
    --query "SecurityGroups[*].IpPermissions[?FromPort==\`8000\` && ToPort==\`8000\`]" \
    --output text)

if [ -n "$PORT_8000_OPEN" ]; then
    echo "✅ Port 8000 is already open"
else
    echo "❌ Port 8000 is NOT open - adding rule..."
    
    # Add rule for port 8000
    aws ec2 authorize-security-group-ingress \
        --group-id "$SG_ID" \
        --protocol tcp \
        --port 8000 \
        --cidr 0.0.0.0/0
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully added port 8000 rule"
    else
        echo "❌ Failed to add port 8000 rule"
    fi
fi

echo ""
echo "5. Testing connectivity after security group update..."
sleep 5
curl -v http://54.165.14.238:8000/health 