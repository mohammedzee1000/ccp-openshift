"""
This file contains operational Openshift clients
"""

from ccp.lib.clients.base import CmdClient
import ccp.lib.utils


class OpenshiftCmdClient(CmdClient):
    """
    Basic openshift client
    """

    def __init__(self, core_cmd_flags=None):
        self.core_oc_cmd = "/usr/bin/oc{}".format(
            " {}".format(core_cmd_flags) if core_cmd_flags else ""
        )

    def get_jenkins_service_account_token(self):
        """
        Queries and gets the Jenkins token. This assumes you have access to oc
        command line.
        :raises Exception
        :return: The token, if it was able to get it. Else, it returns None
        """
        token_cmd = """{core_oc_cmd} get sa/jenkins --template='{template1}' | \
        xargs -n 1 {core_oc_cmd} get secret --template='{template2}' | \
        head -n 1 | base64 -d -\
        """.format(
            core_oc_cmd=self.core_oc_cmd,
            template1="{{range .secrets}}{{ .name }} {{end}}",
            template2="{{ if .data.token }}{{ .data.token }}{{end}}"
        )
        out, ex = ccp.lib.utils.run_cmd(token_cmd, shell=True, use_pipes=True)
        if ex:
            raise Exception("Failed to get token due to {}".format(ex))
        else:
            if out:
                return out.strip()
            return None

    def oc_process(
            self, params, template_file, verbose=True, apply_processed=True
    ):
        """
        Processes a openshift template with appropriate parameters and applies
        them, if needed
        :param params: The dict containing the parameters to apply.
        :type params dict
        :param template_file: The path of template file to process
        :type template_file str
        :param verbose: Default True, if true, prints message on terminal
        :type verbose bool
        :param apply_processed: Default True: Applies the processed template
        :type apply_processed: bool
        :raises Exception
        :return: The output of the run command, if successful
        """
        parameters = ""
        if params and isinstance(params, dict):
            for k, v in params:
                parameters = "{} -p {}={}".format(
                    parameters, k, v
                )
        shell = apply_processed
        use_pipes = apply_processed

        cmd = "{corecommand} process{parameters} -f {template_file}{apply_cmd}"
        cmd = cmd.format(
            corecommand=self.core_oc_cmd,
            parameters=parameters,
            template_file=template_file,
            apply_cmd="| oc apply -f -" if apply_processed else ""
        )
        if verbose:
            print(
                "Applying template {}".format(template_file)
            )
        out, ex = ccp.lib.utils.run_cmd(
            cmd=cmd, shell=shell, use_pipes=use_pipes
        )
        if ex:
            raise Exception("Failed to get token due to {}".format(ex))
        else:
            if out:
                return out.strip()
            return None

    def oc_start_build(self, build_name, namespace, verbose=True):
        """
        Starts a specified build in a specified namespace
        :param build_name: The name of the build to start
        :type build_name str
        :param namespace: The namespace to which the build belongs
        :type namespace str
        :param verbose: Default True, if True, prints msg on terminal
        :raises Exception
        :return: The output of the command, if successful
        """
        if verbose:
            print(
                "Starting build {} in {}".format(
                    build_name,
                    namespace
                )
            )
        out, ex = ccp.lib.utils.run_cmd(
            cmd="{corecommand} start-build {build_name} -n {namespace}".format(
                corecommand=self.core_oc_cmd,
                build_name=build_name,
                namespace=namespace
            ),
            use_pipes=True
        )
        if ex:
            raise Exception("Failed to get token due to {}".format(ex))
        else:
            if out:
                return out.strip()
            return None

    def _oc_delete(self, what, which, namespace):
        """
        Deletes a specified object, unless all is used
        :param what: What kind of object to delete
        :type what str
        :param which: Which of the object, do you wish to delete
        :type which str
        :param namespace: The namespace from which, we need to delete
        :type namespace str
        :raises Exception
        :return: Output, if command executes sucessfully, else None
        """
        cmd = "{corecommand} delete -n {namespace} {what} {which}".format(
            corecommand=self.core_oc_cmd,
            what=what,
            namespace=namespace,
            which=which
        )
        out, ex = ccp.lib.utils.run_cmd(
            cmd=cmd,
            use_pipes=True
        )
        if ex:
            raise Exception("Failed to get token due to {}".format(ex))
        else:
            if out:
                return out.strip()
            return None

    def oc_delete_build_configs(self, bc, namespace, verbose=True):
        """
        Deletes specified build configs
        :param bc: The name of the build config to remove
        :type bc str
        :param namespace The namespace, from which you want to remove
        :type namespace str
        :param verbose: Default Truue, if True, prints message on terminal
        :type verbose bool
        :raises Exception
        :return: output, if command executes successfully, else None
        """
        if verbose:
            print(
                "Removing buildconfig {} from namespace {}".format(
                    bc, namespace
                )
            )
        return self._oc_delete(
            "bc",
            bc,
            namespace
        )

    def _oc_get(self, what, which, namespace, extra_args=None):
        """
        Gets specificed object information
        :param what: What object, you want to fetch information about.
        :type what str
        :param which: Which object you want to fetch information about
        :type which str
        :param namespace: Name of namespace, to which object belongs
        :type namespace str
        :param extra_args: Extra arguments of get command
        :type extra_args str
        :raises Exception
        :return: Output, if command was successful, else nothing
        """
        cmd = "{corecommand} get{extra_args} -n {namespace} {what} {which}"
        cmd = cmd.format(
            corecommand=self.core_oc_cmd,
            what=what,
            namespace=namespace,
            which=which,
            extra_args=" {}".format(
                extra_args
            ) if extra_args else ""
        )
        out, ex = ccp.lib.utils.run_cmd(
            cmd=cmd,
            use_pipes=True
        )
        if ex:
            raise Exception("Failed to get token due to {}".format(ex))
        else:
            if out:
                return out.strip()
            return None

    def oc_list_all_build_configs(self, namespace):
        """
        List all available build configs
        :param namespace The namespace from which to get all the build configs
        :type namespace str
        :raises Exception
        :return list of build configs available
        """
        bcs = self._oc_get(
            what="bc",
            which="",
            namespace=namespace,
            extra_args="-o name"
        )
        if not bcs.strip():
            return []
        else:
            return bcs.strip().split("\n")
