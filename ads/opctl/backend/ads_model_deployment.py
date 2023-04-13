#!/usr/bin/env python
# -*- coding: utf-8; -*-

# Copyright (c) 2022, 2023 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

import json
from typing import Dict

from oci.data_science.models import ModelDeployment as OCIModelDeployment

import ads
from ads.common.auth import AuthContext, create_signer
from ads.common.oci_client import OCIClientFactory
from ads.model.deployment import ModelDeployment
from ads.opctl.backend.base import Backend


class ModelDeploymentBackend(Backend):
    def __init__(self, config: Dict) -> None:
        """
        Initialize a ModelDeployment object given config dictionary.

        Parameters
        ----------
        config: dict
            dictionary of configurations
        """
        self.config = config
        self.oci_auth = create_signer(
            config["execution"].get("auth"),
            config["execution"].get("oci_config", None),
            config["execution"].get("oci_profile", None),
        )
        self.auth_type = config["execution"].get("auth")
        self.profile = config["execution"].get("oci_profile", None)
        self.client = OCIClientFactory(**self.oci_auth).data_science

    def apply(self) -> None:
        """
        Deploy model deployment from YAML.
        """
        wait_for_completion = self.config["execution"].get("wait_for_completion")
        max_wait_time = self.config["execution"].get("max_wait_time")
        poll_interval = self.config["execution"].get("poll_interval")
        with AuthContext(auth=self.auth_type, profile=self.profile):
            model_deployment = ModelDeployment.from_dict(self.config)
            model_deployment.deploy(
                wait_for_completion=wait_for_completion,
                max_wait_time=max_wait_time,
                poll_interval=poll_interval,
            )
            print("Model Deployment id: ", model_deployment.model_deployment_id)

    def delete(self) -> None:
        """
        Delete model deployment from OCID.
        """
        model_deployment_id = self.config["execution"].get("run_id")
        wait_for_completion = self.config["execution"].get("wait_for_completion")
        max_wait_time = self.config["execution"].get("max_wait_time")
        poll_interval = self.config["execution"].get("poll_interval")
        with AuthContext(auth=self.auth_type, profile=self.profile):
            model_deployment = ModelDeployment.from_id(model_deployment_id)
            if model_deployment.lifecycle_state in [
                OCIModelDeployment.LIFECYCLE_STATE_DELETED
                or OCIModelDeployment.LIFECYCLE_STATE_DELETING
            ]:
                print(
                    f"Model deployment {model_deployment.model_deployment_id} is either deleted or being deleted."
                )
                return
            if model_deployment.lifecycle_state not in [
                OCIModelDeployment.LIFECYCLE_STATE_ACTIVE,
                OCIModelDeployment.LIFECYCLE_STATE_FAILED,
                OCIModelDeployment.LIFECYCLE_STATE_INACTIVE,
            ]:
                raise Exception(
                    f"Can't delete model deployment {model_deployment.model_deployment_id} when it's in {model_deployment.lifecycle_state} state."
                )
            model_deployment.delete(
                wait_for_completion=wait_for_completion,
                max_wait_time=max_wait_time,
                poll_interval=poll_interval,
            )
            print(
                f"Model Deployment {model_deployment.model_deployment_id} has been deleted."
            )

    def activate(self) -> None:
        """
        Activate model deployment from OCID.
        """
        model_deployment_id = self.config["execution"].get("run_id")
        wait_for_completion = self.config["execution"].get("wait_for_completion")
        max_wait_time = self.config["execution"].get("max_wait_time")
        poll_interval = self.config["execution"].get("poll_interval")
        with AuthContext(auth=self.auth_type, profile=self.profile):
            model_deployment = ModelDeployment.from_id(model_deployment_id)
            if (
                model_deployment.lifecycle_state
                == OCIModelDeployment.LIFECYCLE_STATE_ACTIVE
            ):
                print(
                    f"Model deployment {model_deployment.model_deployment_id} is already active."
                )
                return

            if (
                model_deployment.lifecycle_state
                == OCIModelDeployment.LIFECYCLE_STATE_INACTIVE
            ):
                model_deployment.activate(
                    wait_for_completion=wait_for_completion,
                    max_wait_time=max_wait_time,
                    poll_interval=poll_interval,
                )
                print(
                    f"Model Deployment {model_deployment.model_deployment_id} has been activated."
                )
            else:
                raise Exception(
                    f"Can't activate model deployment {model_deployment.model_deployment_id} when it's in {model_deployment.lifecycle_state} state."
                )

    def deactivate(self) -> None:
        """
        Deactivate model deployment from OCID.
        """
        model_deployment_id = self.config["execution"].get("run_id")
        wait_for_completion = self.config["execution"].get("wait_for_completion")
        max_wait_time = self.config["execution"].get("max_wait_time")
        poll_interval = self.config["execution"].get("poll_interval")
        with AuthContext(auth=self.auth_type, profile=self.profile):
            model_deployment = ModelDeployment.from_id(model_deployment_id)
            if (
                model_deployment.lifecycle_state
                == OCIModelDeployment.LIFECYCLE_STATE_INACTIVE
            ):
                print(
                    f"Model deployment {model_deployment.model_deployment_id} is already inactive."
                )
                return

            if (
                model_deployment.lifecycle_state
                == OCIModelDeployment.LIFECYCLE_STATE_ACTIVE
            ):
                model_deployment.deactivate(
                    wait_for_completion=wait_for_completion,
                    max_wait_time=max_wait_time,
                    poll_interval=poll_interval,
                )
                print(
                    f"Model Deployment {model_deployment.model_deployment_id} has been deactivated."
                )
            else:
                raise Exception(
                    f"Can't deactivate model deployment {model_deployment.model_deployment_id} when it's in {model_deployment.lifecycle_state} state."
                )

    def watch(self) -> None:
        """
        Watch Model Deployment from OCID.
        """
        model_deployment_id = self.config["execution"].get("run_id")
        log_type = self.config["execution"].get("log_type")
        interval = self.config["execution"].get("interval")
        log_filter = self.config["execution"].get("log_filter")
        with AuthContext(auth=self.auth_type, profile=self.profile):
            model_deployment = ModelDeployment.from_id(model_deployment_id)
            model_deployment.watch(
                log_type=log_type, interval=interval, log_filter=log_filter
            )

    def predict(self) -> None:
        ocid = self.config["execution"].get("ocid")
        data = self.config["execution"].get("payload")
        with AuthContext(auth=self.auth_type, profile=self.profile):
            model_deployment = ModelDeployment.from_id(ocid)
            data = json.loads(data)
            print(model_deployment.predict(data))
        # elif "datasciencemodel":
        #     with AuthContext(auth=self.auth_type, profile=self.profile):
        #         import tempfile
        #         with tempfile.TemporaryDirectory() as td:

        #             model = GenericModel.from_model_catalog(ocid, artifact_dir=os.path.join(td, str(uuid.uuid4())), force_overwrite=True)
                    
        #             conda_pack = self.config["execution"].get("conda", None)
        #             if not conda_pack and hasattr(model.metadata_custom, "EnvironmentType") and model.metadata_custom.EnvironmentType == "published" and hasattr(model.metadata_custom, "CondaEnvironmentPath"):
        #                 conda_pack = model.metadata_custom.CondaEnvironmentPath
        #             if conda_pack and "service-conda-packs" not in conda_pack:
        #                 print("install conda pack and activate the conda pack.")
                    
        #             data = json.loads(data)
        #             print(model.verify(data))
        # else:
        #     raise ValueError("Only model ocid or model deployment ocid is supported.")


