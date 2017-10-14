RepoSync: set of tools to keep scattered codebase synced
=========================================================

Introduction
------------

Large project such like Android AOSP contains multiple git repositories which
is difficult to maintain. Repo tool introduced by Google tackles the issue on
dispatching those codebase to developers. But the remaining issue is repo tool
does not automatically sync codebases scatter in different locations. RepoSync
is used in auto-synchronizing such codebases. 

RepoSync uses client-server model. The server can be deployed in any host that
all clients could reach. It features as a transceiver hub to bridge its clients
to communicate. A primary codebase and several co-working codebases are sitting
on the client side. The primary codebase usually contains bare repos to which
co-working codebases push commits. The primary codebase will notify all other
codebases which connected to the same server about a push event, so that they
can issue pull requests and update themselves.

RepoSync can handle connection interruption.

List of contents
----------------

- *reposyncs.py*
- *post-receive*
- *update-post-receive.sh*
- *reposyncc.py*
- *reposyncr.sh*

Usage
-----

Setting up the server is pretty simple. If the codebases are scattered in
different hosts, then run the file *reposyncs.py* on a host that all others
can reach. Basically, the host which hospitals the primary codebase is an good
one. You can configure the ip address and the port on which the server service
should listen in *reposyncs.py*. To keep it running, a suggestion is to register
it in the file */etc/rc.local* by inserting something like "./reposyncs.py &"
and rebooting.

The client side setting takes two parts. Files in use include *post-receive* and
*reposyncc.py*. IP address and port in those files should be configured and
pointed to the server.

Let's say we have a primary codebase **codebase1** which consists of 4 bare git
repositories organized as following:

	          -repo1.git
	         /
	codebase1--repo2.git
			 \
			  -repos--repo3.git
			        \
					 -repo4.git

The file *post-receive* should be sit inside the folder of *codebase1*. And
symbolic links to the *post-receive* file should be placed in the *hooks*
folders under each repo, ./codebase1/repos/repo3.git/hooks/, for example. A
helper *update-post-receive.sh* is provided to assist inserting symbolic links.
With placing *post-receive* and *update-post-receive.sh* in the codebase root
directory, and running the script you are all set for the first part.

In the second part, assuming there are two working codebases **codebase2** and
**codebase3**. They are clones from **codebase1** and they will push/pull
commits to/from **codebase1**. *reposyncc.py* should be placed inside the
folders **codebase2** and **codebase3** and run as daemon service. 
*reposyncr.sh* is provided to keep track of the locations of *reposyncc.py* and
run them as daemon. You can also add this script in */etc/rc.local* to make it
run on booting.

After doing above steps, pushing commits from **codebase2** to **codebase1** on
**master** branch would make **codebase3** get automatically updated and vise
versa.
