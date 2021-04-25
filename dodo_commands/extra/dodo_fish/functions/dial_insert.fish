function dial_insert
    set cmd (dodo dial -g default $argv)
    if test $cmd
        commandline -i $cmd
    end
end
