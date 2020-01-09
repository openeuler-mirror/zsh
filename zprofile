#
# '.zlogout' is similar to `.zlogin', except that it is sourced before `.zshrc'
#

PATH="$PATH:$HOME/bin"
export PATH

[ -f /etc/profile ] && . /etc/profile
