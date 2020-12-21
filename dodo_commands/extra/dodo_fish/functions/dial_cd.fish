function dial_cd
    #   dodo dial $argv | source
	cd (dodo dial -g shift $argv)
    commandline -f repaint
end
