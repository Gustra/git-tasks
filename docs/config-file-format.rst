===========================
 Configuration file format
===========================

Configuration cheat sheet::

    systems:
      openalm:
        type: tuleap
        url: https://tuleap.mydomain.ok/
        credentials: /path/to/credentials-file
        branch-name: tuleap-${id}
        trackers:
          - id: 12345
            status-map:
              fixed: Solved
              start:
                status: Ongoing
                chatops:
                  - my-team-room
                  - project-room
          - 23451
    chatops:
      - name: my-team-room
        type: xmpp
        credentials: /path/to/xmpp-file
      - name: project-room
        type: jabber
        credentials: /path/to/jabber-file
    jobs:
      - name: unit-test
        alias: ut
        url: http://jenkins.ow/start-job ${cwd}

