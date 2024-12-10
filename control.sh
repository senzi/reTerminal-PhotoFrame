#!/bin/bash

case "$1" in
    "start")
        sudo systemctl start photoframe
        echo "相册已启动"
        ;;
    "stop")
        sudo systemctl stop photoframe
        echo "相册已停止"
        ;;
    "restart")
        sudo systemctl restart photoframe
        echo "相册已重启"
        ;;
    "status")
        sudo systemctl status photoframe
        ;;
    *)
        echo "使用方法: "
        echo "./control.sh start   - 启动相册"
        echo "./control.sh stop    - 停止相册"
        echo "./control.sh restart - 重启相册"
        echo "./control.sh status  - 查看状态"
        ;;
esac