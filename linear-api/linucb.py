from abc import abstractclassmethod, abstractmethod
from functools import reduce
from math import sqrt, log
from os import stat
from typing import List, Tuple
from numpy import asarray, dot, matmul, testing
import numpy
from pipe import Pipe, select, transpose
from numpy.random import uniform
from numpy.linalg import pinv as invert_matrix

from phe import PaillierPrivateKey, PaillierPublicKey, generate_paillier_keypair, EncryptedNumber

from data import DataWrapper
from time import time
from random import seed as setseed
from switch import Switch
from recording import Recording, RecursiveMap
from execution_config import ExecutionConfiguration
from tensor import Tensor
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from os import urandom
from pathlib import Path
from numpy.core.fromnumeric import argmax
from random import random, seed, randint, choices


class SeedableRandomGenerator:
    """
    Random number generator able to produces random float and int, with respect to a given seed.
    """

    def __init__(self, seed):
        self.seed = seed

    def random(self, t) -> float:
        """Returns a random float between 0 and 1 includes given a time step."""
        seed(self.seed + t)
        value = random()

        return value

    def randint(self, t, min, max) -> int:
        """
        Returns a random int between min and max includes given a time step.
        """
        seed(self.seed + t)
        value = randint(min, max)
        return value

    def choice(self, items, weights, t):
        """Returns randomly a item contained in a given list of items, with a given probability weights."""
        seed(self.seed + t)
        value = choices(items, weights=weights, k=1)[0]
        return value


LINUCB_ALGORITHM = "linucb"
PLAINTEXT_VERSION = "plaintext-version"
SINGLE_PAILLIER_VERSION = "single-paillier-version"
MASKED_VERSION = "masked-version"

REGULAR_STEPS_SYNC = "regular-steps"
FOUR_STEPS_SYNC = "four-steps"
TWO_STEPS_SYNC = "two-steps"
EACH_STEPS_SYNC = "each-step"
NO_SYNC = "no-sync"


SYNC_VERSIONS = [NO_SYNC, EACH_STEPS_SYNC, TWO_STEPS_SYNC, FOUR_STEPS_SYNC]

def linucb_versions( with_security  : bool ):
    if with_security:
        return [
            (security, sync)
            for security in [PLAINTEXT_VERSION, MASKED_VERSION]
            for sync in SYNC_VERSIONS
        ]
    else:
        return [
            (security, sync)
            for security in [PLAINTEXT_VERSION]
            for sync in SYNC_VERSIONS
        ]

# ------------------------------------------------------------------------
# Keys Function
# ------------------------------------------------------------------------

def paillier_encrypt_tensor(pk: PaillierPublicKey, tensor: Tensor):
    """Return a copy of provided tensor, where  each item has been encrypted under the provided public key."""
    return tensor.map(lambda item: pk.encrypt(item))


def paillier_decrypt_tensor(sk: PaillierPrivateKey, tensor: Tensor):
    """Return a copy of provided tensor, where  each item has been decrypted with the provided secret key."""
    return tensor.map(lambda item: sk.decrypt(item))


import json

AES_GCM_CIPHERTEXT = bytes


def aes_gcm_encrypt_tensor(cipher: AESGCM, nonce, tensor: Tensor) -> AES_GCM_CIPHERTEXT:
    raw_data = json.dumps(tensor.data()).encode()
    return cipher.encrypt(nonce=nonce, data=raw_data, associated_data=b"")


def aes_gcm_decrypt_tensor(cipher: AESGCM, nonce, ciphertext: AES_GCM_CIPHERTEXT) -> Tensor:
    raw_data = cipher.decrypt(nonce=nonce, data=ciphertext, associated_data=b"").decode()
    return Tensor(json.loads(raw_data))


class PaillierKeyManager:
    """Key Object Manager allows to create and load key quickly from file"""

    @staticmethod
    def load_or_create(key_id: str) -> Tuple[PaillierPublicKey, PaillierPrivateKey]:
        # checks that both private and public keys exists, otherwise create a new one
        # and export it
        filename = f"/tmp/{key_id}"
        file = Path(filename)
        if not file.exists():
            pk, sk = generate_paillier_keypair()
            PaillierKeyManager.save(key_id, pk, sk)
            return pk, sk

        # load the public key
        with open(filename) as file:
            line = file.readline()
            n, p, q = line.split(",") | select(lambda v: int(v))
            pk = PaillierPublicKey(n)
            sk = PaillierPrivateKey(pk, p, q)

        return pk, sk

    @staticmethod
    def save(key_id: str, pk: PaillierPublicKey, sk: PaillierPrivateKey):
        filename = f"/tmp/{key_id}"
        with open(filename, "w") as file:
            file.write(f"{pk.n},{sk.p},{sk.q}")


class DataOwnerContext:
    """Context class represents a namespace where any variables can be stored in."""
    pass


class Timer:
    def __init__(self) -> None:
        self.time = 0
        self.start = None

    def __enter__(self, *args):
        self.start = time()

    def __exit__(self, *args):
        self.time += time() - self.start
        self.start = None


class SecurityPolicy:
    """The security policy determines which security guarantees must be applied"""

    def init(self, timer_server: Timer, data_owners: List[DataOwnerContext]): pass

    def time_step_begin(self, time_step, data_owner: DataOwnerContext): pass

    @abstractmethod
    def synchronize(timer_server: Timer, data_owners: List[DataOwnerContext]): pass


class CentralizedAdditionSecurityPolicy(SecurityPolicy):
    def synchronize(self, timer_server: Timer, data_owners: List[DataOwnerContext]):
        # perform the pre-processing stage
        list_A, list_b = [], []
        for data_owner_index, data_owner in enumerate(data_owners):
            with data_owner.timer:
                list_A.append(self.preprocess(data_owner_index, Tensor(data_owner.increase_A.tolist())))
                list_b.append(self.preprocess(data_owner_index, Tensor(data_owner.increase_b.tolist())))

        # call the server to reduce
        with timer_server:
            A, b = self.server(list_A, list_b)

        # perform the post-processing stage
        for data_owner_index, data_owner in enumerate(data_owners):
            with data_owner.timer:
                data_owner.increase_A = numpy.array(self.postprocess(data_owner_index, A).data())
                data_owner.increase_b = numpy.array(self.postprocess(data_owner_index, b).data())

    @abstractclassmethod
    def preprocess(self, data_owner_index, tensor: Tensor) -> Tensor:
        pass

    @abstractclassmethod
    def server(self, listA: List[Tensor], listB: List[Tensor]) -> Tuple[Tensor, Tensor]:
        pass

    @abstractclassmethod
    def postprocess(self, data_owner_index, tensor: Tensor) -> Tensor:
        pass

class PlaintextSecurityPolicy(CentralizedAdditionSecurityPolicy):
    def preprocess(self, data_owner_index, tensor: Tensor) -> Tensor: return tensor

    def server(self, list_A: List[Tensor], list_b: List[Tensor]) -> Tuple[Tensor, Tensor]:
        # sum of A
        A = list_A[0]
        for A_i in list_A[1:]:
            A = A + A_i

        # sum of B
        b = list_b[0]
        for b_i in list_b[1:]:
            b = b + b_i
        return A, b

    def postprocess(self, data_owner_index, tensor: Tensor) -> Tensor: return tensor


class MaskedAdditionSecurityPolicy(CentralizedAdditionSecurityPolicy):
    def __init__(self, M) -> None:
        # creates symmetric keys between each data owners and the server
        self.M = M
        self.ciphers = [
            AESGCM(key=AESGCM.generate_key(256)) for _ in range(M)
        ]
        self.mask_generator = None
        self.masks = {}
        self.nonce = urandom(128)

    def init(self, timer_server: Timer, data_owners: List[DataOwnerContext]):
        # the first data owner creates a random seed that will be given to all other data owners
        with data_owners[0].timer:
            seed = randint(10, 1000)
            data_owners[0].mask_generator = SeedableRandomGenerator(seed)
            encrypted_seed = self.ciphers[0].encrypt(nonce=self.nonce, data=str(seed).encode(), associated_data=b"")

        cipher = self.ciphers[0]
        for data_owner in data_owners[1:]:
            with data_owner.timer:
                decrypted_seed = cipher.decrypt(nonce=self.nonce, data=encrypted_seed, associated_data=b"")
                decrypted_seed = int(decrypted_seed.decode())
                assert decrypted_seed == seed, "The decrypted seed does not correspond to the given seed"
                data_owner.mask_generator = SeedableRandomGenerator(seed=decrypted_seed)

    def time_step_begin(self, time_step, data_owner: DataOwnerContext):
        assert data_owner.mask_generator is not None, 'Time Step begins without a mask generator'
        self.masks[data_owner.index] = data_owner.mask_generator.randint(t=time_step, min=10, max=10000)

    def preprocess(self, data_owner_index, tensor: Tensor) -> AES_GCM_CIPHERTEXT:
        tensor = tensor.map(lambda item: item + self.masks[data_owner_index])
        return aes_gcm_encrypt_tensor(cipher=self.ciphers[data_owner_index], tensor=tensor, nonce=self.nonce)

    def server(self, list_A: List[AES_GCM_CIPHERTEXT], list_b: List[AES_GCM_CIPHERTEXT]) -> Tuple[
        List[AES_GCM_CIPHERTEXT], List[AES_GCM_CIPHERTEXT]]:
        # decrypts the input
        list_A = [
            aes_gcm_decrypt_tensor(cipher=self.ciphers[data_owner_index], ciphertext=ciphertext, nonce=self.nonce)
            for data_owner_index, ciphertext in enumerate(list_A)
        ]
        list_b = [
            aes_gcm_decrypt_tensor(cipher=self.ciphers[data_owner_index], ciphertext=ciphertext, nonce=self.nonce)
            for data_owner_index, ciphertext in enumerate(list_b)
        ]

        # do the addition
        A = reduce(lambda A_i, A_j: A_i + A_j, list_A)
        b = reduce(lambda b_i, b_j: b_i + b_j, list_b)

        # encrypt the results
        list_A = [
            aes_gcm_encrypt_tensor(cipher=cipher, tensor=A, nonce=self.nonce)
            for cipher in self.ciphers
        ]
        list_b = [
            aes_gcm_encrypt_tensor(cipher=cipher, tensor=b, nonce=self.nonce)
            for cipher in self.ciphers
        ]

        return list_A, list_b

    def postprocess(self, data_owner_index, ciphertexts: List[AES_GCM_CIPHERTEXT]) -> AES_GCM_CIPHERTEXT:
        tensor: Tensor = aes_gcm_decrypt_tensor(cipher=self.ciphers[data_owner_index],
                                                ciphertext=ciphertexts[data_owner_index], nonce=self.nonce)
        return tensor.map(lambda item: item - sum(self.masks.values()))


class SinglePaillierSecurityPolicy(CentralizedAdditionSecurityPolicy):
    """All computations are performed using Paillier Cryptosystem."""

    def __init__(self) -> None:
        self.pk, self.sk = PaillierKeyManager.load_or_create("single-paillier-key")

    def preprocess(self, data_owner_index, tensor: Tensor) -> Tensor: return paillier_encrypt_tensor(self.pk, tensor)

    def server(self, list_A: List[Tensor], list_b: List[Tensor]) -> Tuple[Tensor, Tensor]:
        A = reduce(lambda A_i, A_j: A_i + A_j, list_A)
        b = reduce(lambda b_i, b_j: b_i + b_j, list_b)
        return A, b

    def postprocess(self, data_owner_index, tensor: Tensor) -> Tensor: return paillier_decrypt_tensor(self.sk, tensor)


# ----------------------------------------------------------------------------------------------------------------------
# Synchronization Policy
# ----------------------------------------------------------------------------------------------------------------------
class SynchronizationPolicy:
    """Notifies when a algorithm_sync is required."""

    @abstractclassmethod
    def requiredSynchronize(self, time_step): pass

class EachStepSynchronization(SynchronizationPolicy):
    """A algorithm_sync is done every two steps."""

    def requiredSynchronize(self, time_step): return True

class TwoStepSynchronization(SynchronizationPolicy):
    """A algorithm_sync is done every two steps."""

    def requiredSynchronize(self, time_step): return time_step % 2 == 0

class FourStepSynchronization(SynchronizationPolicy):
    """A algorithm_sync is done every two steps."""

    def requiredSynchronize(self, time_step): return time_step % 4 == 0

class RegularStepSynchronization(SynchronizationPolicy):
    """A algorithm_sync is done every two steps."""

    def __init__(self,n): self.n = n
    def requiredSynchronize(self, time_step): return time_step % self.n == 0


class NoSynchronization(SynchronizationPolicy):
    """No algorithm_sync."""

    def requiredSynchronize(self, time_step): return False


# ----------------------------------------------------------------------------------------------------------------------
# LINU-UCB Algorithm
# ----------------------------------------------------------------------------------------------------------------------
def linucb_naive(
        data: DataWrapper,
        recording: Recording,
        execution_config: ExecutionConfiguration,
        security_policy: SecurityPolicy,
        synchronization_policy: SynchronizationPolicy
) -> Recording:
    """Launch the first version of LinUCB"""

    # the pull function need to be parameterized with some seed which is increased at each call
    seed_container = [execution_config.seed]

    def pull(i):
        seed = seed_container[0]
        setseed(seed)
        seed_container[0] += 1
        numpy.random.seed(seed)
        noise = uniform(-data.R, data.R)
        return dot(x[i], data.theta) + noise

    # ------------------------------------------------------------------------
    # DataOwner(s)
    # ------------------------------------------------------------------------
    # To perform the code without relying on multi-threading, we use a Context object which
    # contains all variables used for a single Data Owners.
    data_owners = [DataOwnerContext() for _ in range(data.M)]

    # initialize timer
    timer_server = Timer()
    for data_owner in data_owners:
        data_owner.timer = Timer()



    # initialize the security policy (e.g,. initial secure communication for the rest of the protocol)
    security_policy.init(
        timer_server=timer_server,
        data_owners=data_owners
    )

    # variables used to track the evolution of the algorithm
    _data_by_turn = RecursiveMap( root = {} )
    EXECUTION_TIME_KEY = "execution-time"
    REWARDS = "rewards"
    THETA_MSE = "theta-mse"
    DETAILS = "details"
    SUM = "sum"

    def register_data_for_turn( t ):
        # recording turn-by-turn information
        data_owners_sum_exec_time = sum([data_owner.timer.time for data_owner in data_owners])
        _data_by_turn[[t, REWARDS, DETAILS]] = []
        _data_by_turn[[t, REWARDS, SUM]] = sum([ data_owner.s for data_owner in data_owners ])
        _data_by_turn[[t, THETA_MSE, DETAILS]] = []
        _data_by_turn[[t, EXECUTION_TIME_KEY, "data-owners", DETAILS]] = []
        _data_by_turn[[t, EXECUTION_TIME_KEY, "data-owners", SUM]] = data_owners_sum_exec_time
        for data_owner_index, data_owner in enumerate(data_owners):
            mse_theta = ((data.theta - data_owner.O) ** 2).mean()
            _data_by_turn[[t, THETA_MSE, DETAILS]].append(mse_theta)
            _data_by_turn[[t, REWARDS, DETAILS]].append(data_owner.s)
            _data_by_turn[[t, EXECUTION_TIME_KEY, "data-owners", DETAILS]].append(data_owner.timer.time)
            _data_by_turn[[t, EXECUTION_TIME_KEY, "server"]] = timer_server.time
            _data_by_turn[[t, EXECUTION_TIME_KEY, "sum"]] = timer_server.time + data_owners_sum_exec_time
        _data_by_turn[[t, THETA_MSE, SUM]] = sum(_data_by_turn[[t, THETA_MSE, DETAILS]])

    global_start = time()


    # Initialization: each data owner Pull an arm and initialize variables
    for data_owner_index, (data_owner, x) in enumerate(zip(data_owners, data.X)):
        with data_owner.timer:
            data_owner.index = data_owner_index
            data_owner.x = numpy.asarray(x)
            data_owner.L = max([numpy.linalg.norm(data_owner.x[i]) for i in range(data.K)])
            i = 0
            r = pull(i)
            data_owner.s = r
            data_owner.A = numpy.outer(data_owner.x[i], data_owner.x[i])
            data_owner.b = r * data_owner.x[i]
            data_owner.increase_A = 0
            data_owner.increase_b = 0
            inv = numpy.linalg.inv(data_owner.A + data.gamma * numpy.identity(data.d))
            data_owner.O = inv.dot(data_owner.b)

    # register since an arm has been pulled
    register_data_for_turn(t=1)

    # Exploration - Exploitation: Maximize the cumulative reward
    for t in range(2, data.N):
        # The first stage is to select an arm
        for data_owner_index, data_owner in enumerate(data_owners):
            A = data_owner.A
            b = data_owner.b
            d = data.d
            x = data_owner.x
            gamma = data.gamma
            delta = data.delta
            R = data.R
            L = data_owner.L
            K = data.K

            with data_owner.timer:
                security_policy.time_step_begin(t, data_owner)

                inv = numpy.linalg.inv(A + gamma * numpy.identity(d))
                data_owner.O = inv.dot(b)
                exploration_term = R * sqrt(d * log((1 + (t * L)/gamma)/delta)) + sqrt(gamma) * log(t)

                # list of Bi
                list_B = []
                for i in range(K):
                    list_B.append( x[i].dot(data_owner.O) + exploration_term * sqrt(x[i].dot(inv).dot(x[i])) )

                # Choose one arm among all equal maximums using the random permutation
                max_B = argmax(list_B)
                x_i = x[max_B]
                r = pull(max_B)
                data_owner.s += r
                data_owner.increase_A += numpy.outer(x_i, x_i)
                data_owner.increase_b += r * x_i

        # perform the algorithm_sync if required
        synchronization_required = synchronization_policy.requiredSynchronize( t )
        if synchronization_required:
            security_policy.synchronize(
                timer_server=timer_server,
                data_owners=data_owners
            )

        # Update local variables of each data owner from the synchronization
        for data_owner_index, data_owner in enumerate(data_owners):
            with data_owner.timer:
                data_owner.s += r
                data_owner.A += data_owner.increase_A
                data_owner.b += data_owner.increase_b
                if synchronization_required:
                    data_owner.increase_A = 0
                    data_owner.increase_b = 0

        # recording turn-by-turn information
        register_data_for_turn(t=t)

    # perform the recording
    global_end = time()
    rewards = sum(map(lambda context: context.s, data_owners))
    global_execution_time = global_end - global_start
    iteration = execution_config.iteration
    recording.add_execution_recording(
        algorithm=LINUCB_ALGORITHM,
        execution_config=execution_config,
        algorithm_version=execution_config.algorithm_version,
        iteration=iteration,
        execution_time=global_execution_time,
        rewards=rewards
    )

    recording.add_turn_by_turn_recording(
        algorithm=LINUCB_ALGORITHM,
        algorithm_version=execution_config.algorithm_version,
        iteration=iteration,
        turn_by_turn_data=_data_by_turn
    )

    recording.add_entity_recording(
        algorithm=LINUCB_ALGORITHM,
        algorithm_version=execution_config.algorithm_version,
        iteration=iteration,
        entity="server",
        execution_time=timer_server.time
    )

    for data_owner_index, data_owner in enumerate(data_owners):
        recording.add_entity_recording(
            algorithm=LINUCB_ALGORITHM,
            algorithm_version=execution_config.algorithm_version,
            iteration=iteration,
            entity=f"data-owner-{data_owner_index}",
            execution_time=data_owner.timer.time,
            reward=data_owner.s
        )

    return rewards


def launch_linucb(data: DataWrapper, recording: Recording, execution_config: ExecutionConfiguration):
    assert execution_config.algorithm == LINUCB_ALGORITHM

    # select the algorithm_sync security policy depending on the algorithm version
    security_policy_selector: Switch = Switch()
    security_policy_selector.case(PLAINTEXT_VERSION, lambda: PlaintextSecurityPolicy())
    security_policy_selector.case(SINGLE_PAILLIER_VERSION, lambda: SinglePaillierSecurityPolicy())
    security_policy_selector.case(MASKED_VERSION, lambda: MaskedAdditionSecurityPolicy(M=data.M))
    security_policy = security_policy_selector.run(execution_config.algorithm_security)

    # select the algorithm_sync policy
    synchronization_policy_selector : Switch = Switch()
    synchronization_policy_selector.case(EACH_STEPS_SYNC, lambda: RegularStepSynchronization(n=1))
    synchronization_policy_selector.case(TWO_STEPS_SYNC, lambda:  RegularStepSynchronization(n=2))
    synchronization_policy_selector.case(FOUR_STEPS_SYNC, lambda: RegularStepSynchronization(n=4))
    synchronization_policy_selector.case(NO_SYNC, lambda: NoSynchronization())
    synchronization_policy = synchronization_policy_selector.run(execution_config.algorithm_sync)

    if NO_SYNC == execution_config.algorithm_sync:
        assert type(synchronization_policy) == NoSynchronization

    # launch the execution
    return linucb_naive(
        data=data,
        execution_config=execution_config,
        synchronization_policy=synchronization_policy,
        recording=recording,
        security_policy=security_policy,
    )


if __name__ == "__main__":
    
    for sync in [NO_SYNC, EACH_STEPS_SYNC, TWO_STEPS_SYNC,FOUR_STEPS_SYNC]:
        print("=" * 30, sync, '=' * 30)
        data = DataWrapper.from_file("debug/small_data.json")
        recording = Recording.new(filename="/tmp/test.txt")
        execution_config = ExecutionConfiguration( "linucb", PLAINTEXT_VERSION, sync, 1, 1, 2 )
        reward = launch_linucb(data, recording, execution_config)
        print(sync, reward)
