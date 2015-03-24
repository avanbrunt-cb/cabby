from itertools import imap

import libtaxii.messages_11 as tm11
from libtaxii import constants as const

from .abstract import AbstractClient
from .converters import (
    to_subscription_response_entity, to_content_block_entity,
    to_collection_entities
)
from .utils import (
    pack_content_bindings, get_utc_now, pack_content_binding
)


class Client11(AbstractClient):
    '''Client implementation for TAXII Specification v1.1

    Use :py:meth:`cabby.create_client` to create client instances.
    '''

    taxii_version = const.VID_TAXII_XML_11
    services_version = const.VID_TAXII_SERVICES_11

    def _discovery_request(self, uri):
        request = tm11.DiscoveryRequest(message_id=self._generate_id())
        response = self._execute_request(request, uri=uri)
        return response

    def __subscription_status_request(self, action, collection_name,
            subscription_id=None, uri=None):
        request_parameters = dict(
            message_id = self._generate_id(),
            action = action,
            collection_name = collection_name,
            subscription_id = subscription_id
        )

        request = tm11.ManageCollectionSubscriptionRequest(**request_parameters)
        response = self._execute_request(request, uri=uri,
                service_type=const.SVC_COLLECTION_MANAGEMENT)

        return to_subscription_response_entity(response, version=11)

    def get_subscription_status(self, collection_name, subscription_id=None, uri=None):
        '''Get subscription status from TAXII Collection Management service.

        Sends a subscription request with action 'STATUS'.
        If no `subscription_id` is provided, server will return the list
        of all available subscriptions for a collection with a name
        specified in `collection_name`.

        if `uri` is not provided, client will try to discover services and
        find Collection Management Service among them.

        :param str collection_name: target collection name
        :param str subscription_id: subscription ID (optional)
        :param str uri: URI path to a specific Collection Management service

        :return: subscription information response
        :rtype: :py:class:`cabby.entities.SubscriptionResponse`

        :raises ValueError:
                if URI provided is invalid or schema is not supported
        :raises `cabby.exceptions.UnsuccessfulStatusError`:
                if Status Message received and status_type is not 'SUCCESS'
        :raises `cabby.exceptions.ServiceNotFoundError`:
                if no service found
        :raises `cabby.exceptions.AmbiguousServicesError`:
                more than one service with type specified
        :raises `cabby.exceptions.NoURIProvidedError`:
                no URI provided and client can't discover services
        '''


        return self.__subscription_status_request(const.ACT_STATUS, collection_name,
                subscription_id=subscription_id, uri=uri)


    def pause_subscription(self, collection_name, subscription_id, uri=None):
        '''Pause a subscription.

        Sends a subscription request with action 'PAUSE'.
        Subscription is identified by `collection_name` and `subscription_id`.

        if `uri` is not provided, client will try to discover services and
        find Collection Management Service among them.

        :param str collection_name: target collection name
        :param str subscription_id: subscription ID
        :param str uri: URI path to a specific Collection Management service

        :return: subscription information response
        :rtype: :py:class:`cabby.entities.SubscriptionResponse`
        
        :raises ValueError:
                if URI provided is invalid or schema is not supported
        :raises `cabby.exceptions.UnsuccessfulStatusError`:
                if Status Message received and status_type is not 'SUCCESS'
        :raises `cabby.exceptions.ServiceNotFoundError`:
                if no service found
        :raises `cabby.exceptions.AmbiguousServicesError`:
                more than one service with type specified
        :raises `cabby.exceptions.NoURIProvidedError`:
                no URI provided and client can't discover services
        '''

        return self.__subscription_status_request(const.ACT_PAUSE, collection_name,
                subscription_id=subscription_id, uri=uri)


    def resume_subscription(self, collection_name, subscription_id, uri=None):
        '''Resume a subscription.

        Sends a subscription request with action 'RESUME'.
        Subscription is identified by `collection_name` and `subscription_id`.

        if `uri` is not provided, client will try to discover services and
        find Collection Management Service among them.

        :param str collection_name: target collection name
        :param str subscription_id: subscription ID
        :param str uri: URI path to a specific Collection Management service

        :return: subscription information response
        :rtype: :py:class:`cabby.entities.SubscriptionResponse`
        
        :raises ValueError:
                if URI provided is invalid or schema is not supported
        :raises `cabby.exceptions.UnsuccessfulStatusError`:
                if Status Message received and status_type is not 'SUCCESS'
        :raises `cabby.exceptions.ServiceNotFoundError`:
                if no service found
        :raises `cabby.exceptions.AmbiguousServicesError`:
                more than one service with type specified
        :raises `cabby.exceptions.NoURIProvidedError`:
                no URI provided and client can't discover services
        '''

        return self.__subscription_status_request(const.ACT_RESUME, collection_name,
                subscription_id=subscription_id, uri=uri)


    def unsubscribe(self, collection_name, subscription_id, uri=None):
        '''Unsubscribe from a subscription.

        Sends a subscription request with action 'UNSUBSCRIBE'.
        Subscription is identified by `collection_name` and `subscription_id`.

        if `uri` is not provided, client will try to discover services and
        find Collection Management Service among them.

        :param str collection_name: target collection name
        :param str subscription_id: subscription ID
        :param str uri: URI path to a specific TAXII service

        :return: subscription information response
        :rtype: :py:class:`cabby.entities.SubscriptionResponse`
        
        :raises ValueError:
                if URI provided is invalid or schema is not supported
        :raises `cabby.exceptions.UnsuccessfulStatusError`:
                if Status Message received and status_type is not 'SUCCESS'
        :raises `cabby.exceptions.ServiceNotFoundError`:
                if no service found
        :raises `cabby.exceptions.AmbiguousServicesError`:
                more than one service with type specified
        :raises `cabby.exceptions.NoURIProvidedError`:
                no URI provided and client can't discover services
        '''

        return self.__subscription_status_request(const.ACT_UNSUBSCRIBE, collection_name,
                subscription_id=subscription_id, uri=uri)


    def subscribe(self, collection_name, count_only=False, inbox_service=None,
            content_bindings=None, uri=None):
        '''Create a subscription.

        Sends a subscription request with action 'SUBSCRIBE'.

        if `uri` is not provided, client will try to discover services and
        find Collection Management Service among them.

        :param str collection_name: target collection name
        :param bool count_only: subscribe only to counts and not full content
        :param `cabby.entities.InboxService` inbox_service:
                Inbox Service that will accept content pushed by TAXII Server
                in the context of this subscription
        :param list content_bindings: a list of strings or
                :py:class:`cabby.entities.ContentBinding` entities
        :param str uri: URI path to a specific Collection Management service

        :return: subscription information response
        :rtype: :py:class:`cabby.entities.SubscriptionResponse`
        
        :raises ValueError:
                if URI provided is invalid or schema is not supported
        :raises `cabby.exceptions.UnsuccessfulStatusError`:
                if Status Message received and status_type is not 'SUCCESS'
        :raises `cabby.exceptions.ServiceNotFoundError`:
                if no service found
        :raises `cabby.exceptions.AmbiguousServicesError`:
                more than one service with type specified
        :raises `cabby.exceptions.NoURIProvidedError`:
                no URI provided and client can't discover services
        '''

        sparams = tm11.SubscriptionParameters(
            response_type = const.RT_COUNT_ONLY if count_only else const.RT_FULL,
            content_bindings = pack_content_bindings(content_bindings, version=11)
        )
        rparams = dict(
            message_id = self._generate_id(),
            action = const.ACT_SUBSCRIBE,
            collection_name = collection_name,
            subscription_parameters = sparams,
        )

        if inbox_service:
            rparams['push_parameters'] = tm11.PushParameters(
                inbox_protocol = inbox_service.protocol,
                inbox_address = inbox_service.address,
                delivery_message_binding = inbox_service.message_bindings[0] if inbox_service.message_bindings else ''
            )

        request = tm11.ManageCollectionSubscriptionRequest(**rparams)
        response = self._execute_request(request, uri=uri, service_type=const.SVC_COLLECTION_MANAGEMENT)

        return to_subscription_response_entity(response, version=11)


    def get_collections(self, uri=None):
        '''Get collections from Collection Management Service.

        if `uri` is not provided, client will try to discover services and
        find Collection Management Service among them.

        :param str uri: URI path to a specific Collection Management service

        :return: list of collections
        :rtype: list of :py:class:`cabby.entities.Collection`
        
        :raises ValueError:
                if URI provided is invalid or schema is not supported
        :raises `cabby.exceptions.UnsuccessfulStatusError`:
                if Status Message received and status_type is not 'SUCCESS'
        :raises `cabby.exceptions.ServiceNotFoundError`:
                if no service found
        :raises `cabby.exceptions.AmbiguousServicesError`:
                more than one service with type specified
        :raises `cabby.exceptions.NoURIProvidedError`:
                no URI provided and client can't discover services
        '''

        request = tm11.CollectionInformationRequest(message_id=self._generate_id())
        response = self._execute_request(request, uri=uri,
                service_type=const.SVC_COLLECTION_MANAGEMENT)

        return to_collection_entities(response.collection_informations, version=11)



    def push(self, content, content_binding, collections_names=None,
            timestamp=None, uri=None):
        '''Push content into Inbox Service.

        if `uri` is not provided, client will try to discover services and
        find Inbox Service among them.

        :param str content: content to push
        :param content_binding: content binding for a content
        :type content_binding: string or :py:class:`cabby.entities.ContentBinding`
        :param list collection_names:
                destination collection names
        :param datetime timestamp: timestamp label of the content block
                (current UTC time by default)
        :param str uri: URI path to a specific Inbox Service

        :raises ValueError:
                if URI provided is invalid or schema is not supported
        :raises `cabby.exceptions.UnsuccessfulStatusError`:
                if Status Message received and status_type is not 'SUCCESS'
        :raises `cabby.exceptions.ServiceNotFoundError`:
                if no service found
        :raises `cabby.exceptions.AmbiguousServicesError`:
                more than one service with type specified
        :raises `cabby.exceptions.NoURIProvidedError`:
                no URI provided and client can't discover services
        '''

        content_block = tm11.ContentBlock(
            content = content,
            content_binding = pack_content_binding(content_binding, version=11),
            timestamp_label = timestamp or get_utc_now()
        )

        inbox_message = tm11.InboxMessage(message_id=self._generate_id(),
                content_blocks=[content_block])

        if collections_names:
            inbox_message.destination_collection_names.extend(collections_names)

        self._execute_request(inbox_message, uri=uri, service_type=const.SVC_INBOX)

        self.log.debug("Content successfully pushed")



    def poll(self, collection_name, begin_date=None, end_date=None, count_only=False,
            subscription_id=None, inbox_service=None, content_bindings=None, uri=None):
        '''Poll content from Polling Service.

        if `uri` is not provided, client will try to discover services and
        find Polling Service among them.

        :param str collection_name: collection to poll
        :param datetime begin_date:
                ask only for content blocks created after `begin_date` (exclusive)
        :param datetime end_date:
                ask only for content blocks created before `end_date` (inclusive)
        :param bool count_only: ask only for counts and not full content
        :param str subsctiption_id: ID of the existing subscription
        :param `cabby.entities.InboxService` inbox_service:
                Inbox Service that will accept content pushed by TAXII Server
                in the context of this Poll Request
        :param list content_bindings:
                list of stings or :py:class:`cabby.entities.ContentBinding` objects
        :param str uri: URI path to a specific Inbox Service

        :raises ValueError:
                if URI provided is invalid or schema is not supported
        :raises `cabby.exceptions.UnsuccessfulStatusError`:
                if Status Message received and status_type is not 'SUCCESS'
        :raises `cabby.exceptions.ServiceNotFoundError`:
                if no service found
        :raises `cabby.exceptions.AmbiguousServicesError`:
                more than one service with type specified
        :raises `cabby.exceptions.NoURIProvidedError`:
                no URI provided and client can't discover services
        '''

        data = dict(
            message_id = self._generate_id(),
            collection_name = collection_name,
            exclusive_begin_timestamp_label = begin_date,
            inclusive_end_timestamp_label = end_date
        )

        if subscription_id:
            data['subscription_id'] = subscription_id
        else:
            poll_params = {
                'content_bindings' : pack_content_bindings(content_bindings, version=11)
            }

            if inbox_service:
                message_bindings = inbox_service.message_bindings[0] \
                        if inbox_service.message_bindings else []

                poll_params['delivery_parameters'] = tm11.DeliveryParameters(
                    inbox_protocol = inbox_service.protocol,
                    inbox_address = inbox_service.address,
                    delivery_message_binding = message_bindings
                )
                poll_params['allow_asynch'] = True

            if count_only:
                poll_params['response_type'] = const.RT_COUNT_ONLY

            data['poll_parameters'] = tm11.PollRequest.PollParameters(**poll_params)

        request = tm11.PollRequest(**data)
        response = self._execute_request(request, uri=uri, service_type=const.SVC_POLL)

        for block in imap(to_content_block_entity, response.content_blocks):
            yield block

        while response.more:
            part = response.result_part_number + 1
            for block in self.fulfilment(collection_name, response.result_id,
                    part_number=part, uri=uri):
                yield block


    def fulfilment(self, collection_name, result_id, part_number=1, uri=None):
        '''Poll content from Polling Service as a part of fulfilment process.

        if `uri` is not provided, client will try to discover services and
        find Polling Service among them.

        :param str collection_name: collection to poll
        :param str result_id: existing polling Result ID
        :param int part_number: index number of a part from the result set
        :param str uri: URI path to a specific Inbox Service

        :raises ValueError:
                if URI provided is invalid or schema is not supported
        :raises `cabby.exceptions.UnsuccessfulStatusError`:
                if Status Message received and status_type is not 'SUCCESS'
        :raises `cabby.exceptions.ServiceNotFoundError`:
                if no service found
        :raises `cabby.exceptions.AmbiguousServicesError`:
                more than one service with type specified
        :raises `cabby.exceptions.NoURIProvidedError`:
                no URI provided and client can't discover services
        '''

        request = tm11.PollFulfillmentRequest(
            message_id = self._generate_id(),
            collection_name = collection_name,
            result_id = result_id,
            result_part_number = part_number
        )

        response = self._execute_request(request, uri=uri, service_type=const.SVC_POLL)

        for block in imap(to_content_block_entity, response.content_blocks):
            yield block

