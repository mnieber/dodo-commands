function dial_cd_ctrl
    #   dodo dial $argv | source
	cd (dodo dial -g ctrl $argv)
    commandline -f repaint
end
