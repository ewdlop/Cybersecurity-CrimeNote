# ssh-detect.zeek
@load base/protocols/ssh

event ssh_auth_success(c: connection, user: string)
{
    print fmt("SSH connection from %s to %s with user %s", c$id$orig_h, c$id$resp_h, user);
}
