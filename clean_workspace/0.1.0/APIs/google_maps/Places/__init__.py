from common_utils.print_log import print_log
# google_maps/Places/__init__.py
from google_maps.SimulationEngine.db import DB
from google_maps.SimulationEngine.utils import _haversine_distance
from typing import Optional, Dict, Any


def autocomplete(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates returning autocomplete predictions for a given input query.

    Args:
        request_data (Dict[str, Any]): Input parameters for the autocomplete request.
            - input (str): The text entered by the user to generate predictions.
            - inputOffset (Optional[int]): Offset from the beginning of the input string to interpret for prediction.
            - languageCode (Optional[str]): Preferred language for prediction results.
            - regionCode (Optional[str]): Unicode region code to influence results.
            - sessionToken (Optional[str]): Token used for session-scoped billing and grouping.
            - includeQueryPredictions (Optional[bool]): Whether to include predictions that complete the entire query.
            - includePureServiceAreaBusinesses (Optional[bool]): Whether to include service-area-only businesses.
            - includedPrimaryTypes (Optional[List[str]]): List of place types to restrict the predictions to.
            - includedRegionCodes (Optional[List[str]]): Restrict results to these CLDR region codes.
            - origin (Optional[Dict[str, float]]): Geographic location of the user.
                - latitude (float)
                - longitude (float)
            - locationRestriction (Optional[Dict[str, Any]]): Restricts predictions to a circular area.
                - circle (Dict[str, Any]):
                    - radius (float): Radius of the restriction in meters.

    Returns:
        Dict[str, Any]: A dictionary representing autocomplete prediction suggestions.

            - suggestions (List[Dict[str, Any]]): List of prediction results.
                - placePrediction (Dict[str, Any]): Details for predicted places.
                    - place (str): Textual display name for the predicted place.
                    - placeId (str): Unique identifier for the place.
                    - distanceMeters (int): Distance from origin to the place in meters.
                    - types (List[str]): Types associated with the place.
                - queryPrediction (Dict[str, Any]): Full query predictions.
                    - text (Dict[str, Any]):
                        - text (str): Predicted full query text.
                        - matches (List[Dict[str, int]]): Substring match details.
                            - startOffset (int): Start position of matched substring.
                            - endOffset (int): End position of matched substring.
    """

    # In a real implementation, you would validate and process request_data here.
    print_log("Called autocomplete with request_data:", request_data)
    # Return the (empty) schema structure for autocomplete response.
    return {}


def get(
    name: str,
    languageCode: Optional[str] = None,
    sessionToken: Optional[str] = None,
    regionCode: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieves detailed information about a place using its resource name.

    Args:
        name (str): Required. The resource name of the place in the format "places/{place_id}".
        languageCode (Optional[str]): Preferred language for localized content if available.
        sessionToken (Optional[str]): Autocomplete session token for billing. Must be base64-safe and <= 36 ASCII chars.
        regionCode (Optional[str]): Unicode CLDR region code to influence localized place details.

    Returns:
        Dict[str, Any]: A dictionary containing all available place details.

            - id (str): Unique place identifier.
            - name (str): Name of the place.
            - rating (float): Average user rating.
            - userRatingCount (int): Number of user ratings.
            - formattedAddress (str): Full formatted address.
            - shortFormattedAddress (str): Abbreviated address format.
            - adrFormatAddress (str): HTML-structured address.
            - primaryType (str): Main classification type.
            - types (List[str]): All associated place types.
            - pureServiceAreaBusiness (bool): Indicates a service-only business.
            - businessStatus (str): Operational status (e.g., OPERATIONAL).
            - priceLevel (str): Relative cost category.
            - utcOffsetMinutes (int): Time zone offset from UTC.
            - internationalPhoneNumber (str): International phone format.
            - nationalPhoneNumber (str): Localized phone number.
            - googleMapsUri (str): Link to place on Google Maps.
            - websiteUri (str): Place's website URL.
            - iconMaskBaseUri (str): Base URI for icon imagery.
            - iconBackgroundColor (str): Icon background color code.

            - allowsDogs (bool): Whether pets are allowed.
            - goodForChildren (bool): Child-friendly status.
            - goodForGroups (bool): Suitable for groups.
            - goodForWatchingSports (bool): Suitable for watching sports.
            - dineIn (bool): Dine-in option available.
            - delivery (bool): Delivery service available.
            - takeout (bool): Takeout service available.
            - curbsidePickup (bool): Curbside pickup available.
            - reservable (bool): Reservations supported.
            - servesBreakfast (bool): Serves breakfast.
            - servesLunch (bool): Serves lunch.
            - servesBrunch (bool): Serves brunch.
            - servesDinner (bool): Serves dinner.
            - servesCoffee (bool): Coffee served.
            - servesDessert (bool): Serves dessert.
            - servesBeer (bool): Serves beer.
            - servesWine (bool): Serves wine.
            - servesCocktails (bool): Serves cocktails.
            - servesVegetarianFood (bool): Vegetarian options available.
            - menuForChildren (bool): Children's menu offered.
            - liveMusic (bool): Live music available.
            - restroom (bool): Restroom facilities available.

            - paymentOptions (Dict[str, bool]): Accepted payment methods.
                - acceptsCashOnly (bool): Accepts only cash.
                - acceptsCreditCards (bool): Accepts credit cards.
                - acceptsDebitCards (bool): Accepts debit cards.
                - acceptsNfc (bool): Accepts NFC payments.

            - accessibilityOptions (Dict[str, bool]): Accessibility features.
                - wheelchairAccessibleEntrance (bool)
                - wheelchairAccessibleRestroom (bool)
                - wheelchairAccessibleParking (bool)
                - wheelchairAccessibleSeating (bool)

            - primaryTypeDisplayName (Dict[str, str]): Localized type name.
                - text (str): Display label.
                - languageCode (str): Language of label.

            - location (Dict[str, float]): Geographic coordinates.
                - latitude (float)
                - longitude (float)

            - reviewSummary (Dict[str, str]):
                - flagContentUri (str): URI to flag review summary content.

            - currentOpeningHours (Dict[str, Any]): Operating schedule details.
                - openNow (bool): Whether the place is open.
                - secondaryHoursType (str): Type of alternate hours.
                - nextOpenTime (str): ISO time for next open.
                - nextCloseTime (str): ISO time for next close.
                - weekdayDescriptions (List[str]): Human-readable daily hours.
                - periods (List[Dict[str, Any]]): Time blocks for each day.
                    - open (Dict[str, Any]):
                        - day (int)
                        - hour (int)
                        - minute (int)
                        - truncated (bool)
                - specialDays (List[Dict[str, Any]]): Special openings/closures.
                    - date (Dict[str, int]):
                        - day (int)
                        - month (int)
                        - year (int)

            - attributions (List[Dict[str, str]]): Data providers.
                - provider (str)
                - providerUri (str)

            - generativeSummary (Dict[str, str]):
                - overviewFlagContentUri (str): Flag URI for summary.

            - neighborhoodSummary (Dict[str, str]):
                - flagContentUri (str): Flag URI for neighborhood section.

            - postalAddress (Dict[str, Any]): Complete structured address.
                - addressLines (List[str])
                - recipients (List[str])
                - sublocality (str)
                - postalCode (str)
                - organization (str)
                - revision (int)
                - locality (str)
                - administrativeArea (str)
                - languageCode (str)
                - regionCode (str)
                - sortingCode (str)

            - plusCode (Dict[str, str]): Open location code.
                - globalCode (str)
                - compoundCode (str)

            - googleMapsLinks (Dict[str, str]): Google Maps links.
                - photosUri (str)
                - writeAReviewUri (str)
                - placeUri (str)
                - reviewsUri (str)
                - directionsUri (str)

            - subDestinations (List[Dict[str, str]]): Sub-places within the entity.
                - name (str)
                - id (str)

            - containingPlaces (List[Dict[str, str]]): Parent or container places.
                - name (str)
                - id (str)

            - photos (List[Dict[str, Any]]): Associated photos.
                - name (str)
                - widthPx (int)
                - heightPx (int)
                - googleMapsUri (str)
                - flagContentUri (str)

            - addressComponents (List[Dict[str, Any]]): Address components.
                - longText (str)
                - shortText (str)
                - languageCode (str)
                - types (List[str])

            - addressDescriptor (Dict[str, Any]): Location context descriptors.
                - areas (List[Dict[str, str]]): Contained area information.
                    - name (str)
                    - placeId (str)
                    - containment (str)
                - landmarks (List[Dict[str, Any]]): Nearby landmarks.
                    - placeId (str)
                    - name (str)
                    - spatialRelationship (str)
                    - straightLineDistanceMeters (float)
                    - travelDistanceMeters (float)
                    - types (List[str])

            - reviews (List[Dict[str, Any]]): Reviews by users.
                - name (str)
                - googleMapsUri (str)
                - flagContentUri (str)
                - rating (float)
                - relativePublishTimeDescription (str)
                - publishTime (str)
                - authorAttribution (Dict[str, str]):
                    - displayName (str)
                    - photoUri (str)
                    - uri (str)

            - fuelOptions (Dict[str, Any]): Fuel pricing details.
                - fuelPrices (List[Dict[str, str]]):
                    - type (str)
                    - updateTime (str)

            - priceRange (Dict[str, Any]): Price tier estimates.
                - endPrice (Dict[str, Union[int, str]]):
                    - nanos (int)
                    - currencyCode (str)
                    - units (str)

            - evChargeOptions (Dict[str, Any]): EV charger availability.
                - connectorCount (int)
                - connectorAggregation (List[Dict[str, Any]]):
                    - availabilityLastUpdateTime (str)
                    - availableCount (int)
                    - outOfServiceCount (int)
                    - maxChargeRateKw (float)
                    - type (str)
                    - count (int)

            - evChargeAmenitySummary (Dict[str, Any]):
                - flagContentUri (str)
                - store (Dict[str, List[str]]):
                    - referencedPlaces (List[str])

            - parkingOptions (Dict[str, bool]): Parking availability.
                - paidGarageParking (bool)
                - valetParking (bool)
                - paidParkingLot (bool)
                - freeStreetParking (bool)
                - freeGarageParking (bool)
                - freeParkingLot (bool)
                - paidStreetParking (bool)

            - timeZone (Dict[str, str]): Time zone data.
                - id (str)
                - version (str)

    Raises:
        ValueError: If `name` is not in the correct "places/{place_id}" format.
    """

    # Validate that the name matches the expected format.
    if not name.startswith("places/"):
        raise ValueError("Resource name must be in the format 'places/{place_id}'.")

    # Extract the place_id from the name.
    place_id = name.split("/")[1]

    return DB.get(place_id, None)


def searchNearby(request: Dict[str, Any]) -> Dict[str, Any]:
    """Searches for places in the static database based on provided filters.

    Filters can include primary types, secondary types (included or excluded),
    a specific language code for the display name, and a geographical
    location restriction with a center point and a radius.

    Args:
        request (Dict[str, Any]): A dictionary containing the search parameters.
            Expected keys:
            - 'includedPrimaryTypes' (Optional[List[str]]): Only return places that have at least one of these primary types. Primary types are defined in (https://developers.google.com/maps/documentation/places/web-service/place-types)
            - 'excludedPrimaryTypes' (Optional[List[str]]): Do not return places that have any of these primary types. Primary types are defined in (https://developers.google.com/maps/documentation/places/web-service/place-types)
            - 'includedTypes' (Optional[List[str]]): Only return places that have at least one of these types (primary or secondary). Types are defined in (https://developers.google.com/maps/documentation/places/web-service/place-types)
            - 'excludedTypes' (Optional[List[str]]): Do not return places that have any of these types (primary or secondary). Types are defined in (https://developers.google.com/maps/documentation/places/web-service/place-types)
            - 'languageCode' (Optional[str]): The preferred language for the displayName. If provided, only places with a displayName in this language will be returned.
            - 'locationRestriction' (Optional[Dict[str, Any]]): Limits the search to a circular area.
                - 'circle' (Optional[Dict[str, float]]): Defines the circle.
                - 'center' (Dict[str, float]): The center of the circle.
                    - 'latitude' (float): The latitude of the center point.
                    - 'longitude' (float): The longitude of the center point.
                - 'radius' (float): The radius of the circle in meters.
            - 'maxResultCount' (int, optional): The maximum number of places to return.
                Defaults to 20.
            - 'regionCode' (str, optional): Unicode country/region code of the request origin.
            - 'rankPreference' (str, optional): Specifies the ranking of the results.
                One of:
                - "RANK_PREFERENCE_UNSPECIFIED"
                - "DISTANCE"
                - "POPULARITY"
            - 'routingParameters' (Optional[Dict[str, Any]]): Parameters to configure routing calculations.
                - 'routingPreference' (Optional[str]): Specifies how to compute routing summaries.
                    One of:
                    - "ROUTING_PREFERENCE_UNSPECIFIED": No routing preference specified. Defaults to `TRAFFIC_UNAWARE`.
                    - "TRAFFIC_UNAWARE": Ignores live traffic conditions. Optimized for lowest latency.
                    - "TRAFFIC_AWARE": Considers live traffic, but includes some performance optimizations.
                    - "TRAFFIC_AWARE_OPTIMAL": Fully considers live traffic without optimizations (highest latency).
                - 'routeModifiers' (Optional[Dict[str, bool]]): Conditions to avoid in routing.
                    - 'avoidFerries' (Optional[bool]): Avoid ferries when possible.
                    - 'avoidTolls' (Optional[bool]): Avoid toll roads when possible.
                    - 'avoidIndoor' (Optional[bool]): Avoid indoor navigation when possible.
                    - 'avoidHighways' (Optional[bool]): Avoid highways when possible.
                - 'origin' (Optional[Dict[str, float]]): Overrides the polyline origin.
                    - 'latitude' (float): Latitude in degrees. Range: [-90.0, +90.0].
                    - 'longitude' (float): Longitude in degrees. Range: [-180.0, +180.0].
                - 'travelMode' (Optional[str]): Specifies the mode of travel.
                    One of:
                    - "TRAVEL_MODE_UNSPECIFIED": No travel mode specified. Defaults to `DRIVE`.
                    - "DRIVE": Travel by passenger car.
                    - "BICYCLE": Travel by bicycle. Not supported with `search_along_route_parameters`.
                    - "WALK": Travel by walking. Not supported with `search_along_route_parameters`.
                    - "TWO_WHEELER": Motorized two-wheeled vehicles like scooters or motorcycles. Only supported in specific countries.


    Returns:
        Dict[str, Any]: A dictionary containing matched places and associated routing summaries.

            - places (List[Dict[str, Any]]): List of place results.
                - id (str): Unique place identifier.
                - name (str): Display name of the place.
                - rating (float): Average user rating.
                - userRatingCount (int): Total number of ratings.
                - formattedAddress (str): Full readable address.
                - shortFormattedAddress (str): Abbreviated address.
                - adrFormatAddress (str): Address in HTML format.
                - primaryType (str): Main type category.
                - types (List[str]): All associated place types.
                - pureServiceAreaBusiness (bool): True if no physical location.
                - businessStatus (str): Operational status.
                - priceLevel (str): Price level from free to very expensive.
                - utcOffsetMinutes (int): Time zone offset in minutes.
                - internationalPhoneNumber (str): Phone number with country code.
                - nationalPhoneNumber (str): Regional phone number format.
                - googleMapsUri (str): Link to the place on Google Maps.
                - websiteUri (str): Website URL of the place.
                - iconMaskBaseUri (str): Base URI for place icon.
                - iconBackgroundColor (str): Icon background hex color.

                - allowsDogs (bool): True if dogs are allowed.
                - goodForChildren (bool): True if child-friendly.
                - goodForGroups (bool): Suitable for group visits.
                - goodForWatchingSports (bool): Good for watching sports.
                - dineIn (bool): Dine-in available.
                - delivery (bool): Delivery service offered.
                - takeout (bool): Takeout available.
                - curbsidePickup (bool): Supports curbside pickup.
                - reservable (bool): Reservations accepted.
                - servesBreakfast (bool): Serves breakfast.
                - servesLunch (bool): Serves lunch.
                - servesBrunch (bool): Serves brunch.
                - servesDinner (bool): Serves dinner.
                - servesCoffee (bool): Coffee available.
                - servesDessert (bool): Dessert available.
                - servesBeer (bool): Serves beer.
                - servesWine (bool): Serves wine.
                - servesCocktails (bool): Serves cocktails.
                - servesVegetarianFood (bool): Has vegetarian options.
                - menuForChildren (bool): Has children's menu.
                - liveMusic (bool): Offers live music.

                - paymentOptions (Dict[str, bool]): Accepted payment methods.
                    - acceptsCashOnly (bool): Accepts only cash.
                    - acceptsCreditCards (bool): Accepts credit cards.
                    - acceptsDebitCards (bool): Accepts debit cards.
                    - acceptsNfc (bool): Accepts NFC payments.

                - accessibilityOptions (Dict[str, bool]): Accessibility support.
                    - wheelchairAccessibleEntrance (bool)
                    - wheelchairAccessibleRestroom (bool)
                    - wheelchairAccessibleParking (bool)
                    - wheelchairAccessibleSeating (bool)

                - primaryTypeDisplayName (Dict[str, str]): Localized display info.
                    - text (str): Display text.
                    - languageCode (str): Language code of display name.

                - location (Dict[str, float]): Geographic coordinates.
                    - latitude (float)
                    - longitude (float)

                - reviewSummary (Dict[str, str]):
                    - flagContentUri (str): URI to report summary issues.

                - currentOpeningHours (Dict[str, Any]): Opening hours data.
                    - openNow (bool): Currently open or not.
                    - secondaryHoursType (str): Secondary hours category.
                    - nextOpenTime (str): ISO timestamp of next opening.
                    - nextCloseTime (str): ISO timestamp of next closing.
                    - weekdayDescriptions (List[str]): Human-friendly weekday hours.
                    - periods (List[Dict[str, Any]]): Opening/closing time blocks.
                        - open (Dict[str, Any]):
                            - day (int)
                            - hour (int)
                            - minute (int)
                            - truncated (bool): If truncated for display.
                    - specialDays (List[Dict[str, Any]]): Special openings.
                        - date (Dict[str, int]):
                            - day (int)
                            - month (int)
                            - year (int)

                - attributions (List[Dict[str, str]]): Content provider credits.
                    - provider (str): Name of provider.
                    - providerUri (str): Link to the provider.

                - generativeSummary (Dict[str, str]):
                    - overviewFlagContentUri (str): Report AI summary content.

                - neighborhoodSummary (Dict[str, str]):
                    - flagContentUri (str): Report neighborhood summary issues.

                - postalAddress (Dict[str, Any]): Structured address fields.
                    - addressLines (List[str])
                    - recipients (List[str])
                    - sublocality (str)
                    - postalCode (str)
                    - organization (str)
                    - revision (int)
                    - locality (str)
                    - administrativeArea (str)
                    - languageCode (str)
                    - regionCode (str)
                    - sortingCode (str)

                - plusCode (Dict[str, str]): Global location code.
                    - globalCode (str)
                    - compoundCode (str)

                - googleMapsLinks (Dict[str, str]): Useful Google Maps URIs.
                    - photosUri (str)
                    - writeAReviewUri (str)
                    - placeUri (str)
                    - reviewsUri (str)
                    - directionsUri (str)

                - subDestinations (List[Dict[str, str]]): Sub-entities inside place.
                    - name (str)
                    - id (str)

                - containingPlaces (List[Dict[str, str]]): Parent place data.
                    - name (str)
                    - id (str)

                - photos (List[Dict[str, Any]]): Associated photos.
                    - name (str)
                    - widthPx (int)
                    - heightPx (int)
                    - googleMapsUri (str)
                    - flagContentUri (str)

                - addressComponents (List[Dict[str, Any]]): Address parts.
                    - longText (str)
                    - shortText (str)
                    - languageCode (str)
                    - types (List[str])

                - addressDescriptor (Dict[str, Any]): Additional location details.
                    - areas (List[Dict[str, str]]): Contextual areas.
                        - name (str)
                        - placeId (str)
                        - containment (str)
                    - landmarks (List[Dict[str, Any]]): Notable nearby locations.
                        - placeId (str)
                        - name (str)
                        - spatialRelationship (str)
                        - straightLineDistanceMeters (float)
                        - travelDistanceMeters (float)
                        - types (List[str])

                - reviews (List[Dict[str, Any]]): User-generated reviews.
                    - name (str)
                    - googleMapsUri (str)
                    - flagContentUri (str)
                    - rating (float)
                    - relativePublishTimeDescription (str)
                    - publishTime (str)
                    - authorAttribution (Dict[str, str]):
                        - displayName (str)
                        - photoUri (str)
                        - uri (str)

                - fuelOptions (Dict[str, Any]): Nearby fuel pricing data.
                    - fuelPrices (List[Dict[str, str]]):
                        - type (str)
                        - updateTime (str)

                - priceRange (Dict[str, Any]): Pricing information.
                    - endPrice (Dict[str, Union[int, str]]):
                        - nanos (int)
                        - currencyCode (str)
                        - units (str)

                - evChargeOptions (Dict[str, Any]): EV charger details.
                    - connectorCount (int)
                    - connectorAggregation (List[Dict[str, Any]]):
                        - availabilityLastUpdateTime (str)
                        - availableCount (int)
                        - maxChargeRateKw (float)
                        - outOfServiceCount (int)
                        - type (str)
                        - count (int)

                - evChargeAmenitySummary (Dict[str, Any]): EV summaries.
                    - flagContentUri (str)
                    - store (Dict[str, List[str]]):
                        - referencedPlaces (List[str])

                - parkingOptions (Dict[str, bool]): Parking availability.
                    - paidGarageParking (bool)
                    - valetParking (bool)
                    - paidParkingLot (bool)
                    - freeStreetParking (bool)
                    - freeGarageParking (bool)
                    - freeParkingLot (bool)
                    - paidStreetParking (bool)

                - timeZone (Dict[str, str]): Time zone metadata.
                    - id (str)
                    - version (str)

            - routingSummaries (List[Dict[str, Any]]): Optional travel summaries.
                - directionsUri (str): Link to the directions.
                - legs (List[Dict[str, Any]]): Segmented route steps.
                    - duration (str): Duration of travel.
                    - distanceMeters (int): Travel distance in meters.

    Raises:
        TypeError: If the `request` parameter is not a dictionary.
        ValueError: If the `request` dictionary is missing the
            'locationRestriction' key when location-based filtering is intended,
            or if 'locationRestriction' does not contain a 'circle', or if
            'circle' does not contain 'center' and 'radius', or if 'center'
            does not contain 'latitude' and 'longitude'.
    """
    filtered_places = []
    routing_summaries = []

    # Retrieve maxResultCount, default to 20 if not provided.
    max_result_count = request.get("maxResultCount", 20)
    languageCode = request.get("languageCode", "")

    # Extract filtering parameters from the request.
    included_primary_types = request.get("includedPrimaryTypes", [])
    excluded_primary_types = request.get("excludedPrimaryTypes", [])
    included_types = request.get("includedTypes", [])
    excluded_types = request.get("excludedTypes", [])

    # For location filtering, we expect a locationRestriction with a circle.
    location_restriction = request.get("locationRestriction", {})
    circle = location_restriction.get("circle")
    if circle:
        center = circle.get("center", {})
        radius = circle.get("radius", 0.0)
        center_lat = center.get("latitude")
        center_lon = center.get("longitude")
    else:
        center_lat = center_lon = radius = None

    # Loop over each place in the static DB.
    for place in DB.values():
        # Filter by primary types if provided.
        primary_type = place.get("primaryType")
        if included_primary_types and primary_type not in included_primary_types:
            continue
        if excluded_primary_types and primary_type in excluded_primary_types:
            continue

        if included_types:
            types = place.get("types", [])
            if not any(t in included_types for t in types):
                continue
        if excluded_types:
            types = place.get("types", [])
            if any(t in excluded_types for t in types):
                continue

        if (
            languageCode
            and place.get("displayName", {}).get("languageCode") != languageCode
        ):
            continue

        # If location restriction is provided, filter by distance.
        if center_lat is not None and center_lon is not None and radius is not None:
            place_location = place.get("location", {})
            place_lat = place_location.get("latitude")
            place_lon = place_location.get("longitude")
            if place_lat is None or place_lon is None:
                continue
            distance = _haversine_distance(center_lat, center_lon, place_lat, place_lon)
            if distance > radius:
                continue

        # If the place passes all filters, add it to the result list.
        filtered_places.append(place)

        # Generate a dummy routing summary for this place.
        routing_summary = {}
        routing_summaries.append(routing_summary)

        if len(filtered_places) >= max_result_count:
            break

    return {"places": filtered_places, "routingSummaries": routing_summaries}


def searchText(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Performs a text-based search for places using optional filters.

    This function processes a search request structured according to the
    GoogleMapsPlacesV1SearchTextRequest schema. Supported filters include:
    'strictTypeFiltering', 'priceLevels', 'locationBias', 'openNow',
    'minRating', 'includePureServiceAreaBusinesses', 'locationRestriction',
    'languageCode', 'pageSize', 'regionCode', 'textQuery', and others.

    Args:
        request (Dict[str, Any]): Dictionary with the following keys:
            - textQuery (str): Required text query to search for.
            - pageSize (Optional[int]): Max number of results.
            - maxResultCount (Optional[int]): Alternate to pageSize.
            - strictTypeFiltering (Optional[bool]): If true, only places whose primaryType exactly matches includedType will be returned. Defaults to false.
            - includedType (Optional[str]): Used in conjunction with `strictTypeFiltering=true`. Only return places that have at least one of these types (primary or secondary). Types are defined in (https://developers.google.com/maps/documentation/places/web-service/place-types)
            - priceLevels (Optional[List[str]]): Filter results by the specified price levels.
                Allowed values include:
                - PRICE_LEVEL_UNSPECIFIED
                - PRICE_LEVEL_FREE
                - PRICE_LEVEL_INEXPENSIVE
                - PRICE_LEVEL_MODERATE
                - PRICE_LEVEL_EXPENSIVE
                - PRICE_LEVEL_VERY_EXPENSIVE
            - 'locationBias' (Optional[Dict[str, Any]]): A geographic “bias” that influences result ordering.
                One of:
                - 'circle' (Optional[Dict[str, Any]]): A circular geographic area.
                    - 'center' (Dict[str, float]): Required. The center point of the circle.
                        - 'latitude' (float): The center’s latitude.
                        - 'longitude' (float): The center’s longitude.
                    - 'radius' (float): Required. Radius in meters. Only places within this circle are returned.
                - 'rectangle' (Optional[Dict[str, Any]]): A rectangular geographic area.
                    - 'viewport' (Dict[str, Any]): Required. The bounding box of the rectangle.
                        - 'low' (Dict[str, float]): Required. Southwest point of the viewport.
                            - 'latitude' (float): Latitude of the southwest corner.
                            - 'longitude' (float): Longitude of the southwest corner.
                        - 'high' (Dict[str, float]): Required. Northeast point of the viewport.
                            - 'latitude' (float): Latitude of the northeast corner.
                            - 'longitude' (float): Longitude of the northeast corner.
            - openNow (Optional[bool]): If true, only return places that are currently open. Defaults to false.
            - minRating (Optional[float]): If provided, only return places with a rating greater than or equal to the specified value.
            - pageToken (Optional[str]): Used for pagination. If provided, returns the next set of results following a previous search.
            - includePureServiceAreaBusinesses (Optional[bool]): If false, exclude places that are pure service area businesses. Defaults to true.
            - 'locationRestriction' (Optional[Dict[str, Any]]): Limits the
                search to a circular area.
                - 'circle' (Optional[Dict[str, float]]): Defines the circle.
                - 'center' (Dict[str, float]): The center of the circle.
                    - 'latitude' (float): The latitude of the center point.
                    - 'longitude' (float): The longitude of the center point.
                - 'radius' (float): The radius of the circle in meters.
            - languageCode (Optional[str]): The preferred language for the displayName. If provided, only places with a displayName in this language will be returned.
            - 'regionCode' (Optional[str]): Unicode country/region code of the request origin.
            - 'searchAlongRouteParameters' (Optional[Dict[str, Any]]): Specifies a precalculated polyline route used to bias place search results along a path, rather than in a general area like `locationBias` or `locationRestriction`.
                - 'polyline' (Dict[str, str]): Required. Defines the route polyline.
                    - 'encodedPolyline' (str): An encoded polyline string representing the route, as defined by the [Google Polyline Algorithm](https://developers.google.com/maps/documentation/utilities/polylinealgorithm).
            - 'evOptions' (Optional[Dict[str, Any]]): Electric vehicle (EV) filtering options for the search.
                - 'connectorTypes' (Optional[List[str]]): List of preferred EV connector types. Places without any of the specified connectors are excluded. Valid values include:
                    - "EV_CONNECTOR_TYPE_UNSPECIFIED": Unspecified connector.
                    - "EV_CONNECTOR_TYPE_OTHER": Other connector types.
                    - "EV_CONNECTOR_TYPE_J1772": J1772 type 1 connector.
                    - "EV_CONNECTOR_TYPE_TYPE_2": IEC 62196 type 2 connector (MENNEKES).
                    - "EV_CONNECTOR_TYPE_CHADEMO": CHAdeMO connector.
                    - "EV_CONNECTOR_TYPE_CCS_COMBO_1": Combined Charging System, type-1 J-1772.
                    - "EV_CONNECTOR_TYPE_CCS_COMBO_2": Combined Charging System, type-2 Mennekes.
                    - "EV_CONNECTOR_TYPE_TESLA": Generic Tesla connector. May vary by region (e.g., NACS, CCS2, GB/T).
                    - "EV_CONNECTOR_TYPE_UNSPECIFIED_GB_T": GB/T standard connector (China).
                    - "EV_CONNECTOR_TYPE_UNSPECIFIED_WALL_OUTLET": Unspecified wall outlet.
                    - "EV_CONNECTOR_TYPE_NACS": North American Charging System (NACS), SAE J3400 standard.
                - 'minimumChargingRateKw' (Optional[float]): Minimum charging rate in kilowatts. Filters out places with a lower charging rate.
            - 'routingParameters' (Optional[Dict[str, Any]]): Parameters to configure routing calculations.
                - 'routingPreference' (Optional[str]): Specifies how to compute routing summaries.
                    One of:
                    - "ROUTING_PREFERENCE_UNSPECIFIED": No routing preference specified. Defaults to `TRAFFIC_UNAWARE`.
                    - "TRAFFIC_UNAWARE": Ignores live traffic conditions. Optimized for lowest latency.
                    - "TRAFFIC_AWARE": Considers live traffic, but includes some performance optimizations.
                    - "TRAFFIC_AWARE_OPTIMAL": Fully considers live traffic without optimizations (highest latency).
                - 'routeModifiers' (Optional[Dict[str, bool]]): Conditions to avoid in routing.
                    - 'avoidFerries' (Optional[bool]): Avoid ferries when possible.
                    - 'avoidTolls' (Optional[bool]): Avoid toll roads when possible.
                    - 'avoidIndoor' (Optional[bool]): Avoid indoor navigation when possible.
                    - 'avoidHighways' (Optional[bool]): Avoid highways when possible.
                - 'origin' (Optional[Dict[str, float]]): Overrides the polyline origin.
                    - 'latitude' (float): Latitude in degrees. Range: [-90.0, +90.0].
                    - 'longitude' (float): Longitude in degrees. Range: [-180.0, +180.0].
                - 'travelMode' (Optional[str]): Specifies the mode of travel.
                    One of:
                    - "TRAVEL_MODE_UNSPECIFIED": No travel mode specified. Defaults to `DRIVE`.
                    - "DRIVE": Travel by passenger car.
                    - "BICYCLE": Travel by bicycle. Not supported with `search_along_route_parameters`.
                    - "WALK": Travel by walking. Not supported with `search_along_route_parameters`.
                    - "TWO_WHEELER": Motorized two-wheeled vehicles like scooters or motorcycles. Only supported in specific countries.
            - 'rankPreference' (Optional[str]): Specifies the ranking of the results.
                One of:
                - "RANK_PREFERENCE_UNSPECIFIED"
                - "DISTANCE"
                - "POPULARITY"

    Returns:
        Dict[str, Any]: Dictionary with the following keys:

            - nextPageToken (str): A token used to retrieve the next page of results.
            - searchUri (str): A URI that can be used to replicate the search.
            - routingSummaries (List[Dict[str, Any]]): A list of routing summaries with fields such as:
                - directionsUri (str): URI linking to directions for the route.
                - legs (List[Dict[str, Any]]): Segments of the route.
                    - duration (str): Duration of the leg.
                    - distanceMeters (int): Distance in meters for the leg.
            - places (List[Dict[str, Any]]): List of matching place results. Each dictionary may contain:
                - id (str): Unique identifier for the place.
                - name (str): Name of the place.
                - rating (float): Average user rating.
                - userRatingCount (int): Number of user ratings.
                - formattedAddress (str): Full address in display-friendly format.
                - primaryType (str): The place’s primary classification type.
                - types (List[str]): Additional types describing the place.
                - location (Dict[str, float]): Geographic location of the place.
                    - latitude (float): Latitude coordinate.
                    - longitude (float): Longitude coordinate.
                - businessStatus (str): Current operating status (e.g., OPERATIONAL).
                - priceLevel (str): Price level of the place.
                - openNow (bool): Whether the place is currently open.
                - takeout (bool): If takeout is available.
                - delivery (bool): If delivery is available.
                - dineIn (bool): If dine-in is available.
                - outdoorSeating (bool): If outdoor seating is available.
                - curbsidePickup (bool): If curbside pickup is supported.
                - servesBreakfast (bool): If the place serves breakfast.
                - servesLunch (bool): If the place serves lunch.
                - servesDinner (bool): If the place serves dinner.
                - servesBrunch (bool): If the place serves brunch.
                - servesCoffee (bool): If the place serves coffee.
                - servesDessert (bool): If the place serves dessert.
                - servesBeer (bool): If the place serves beer.
                - servesWine (bool): If the place serves wine.
                - servesCocktails (bool): If the place serves cocktails.
                - goodForChildren (bool): If the place is child-friendly.
                - goodForGroups (bool): If the place is good for groups.
                - goodForWatchingSports (bool): If the place is suitable for watching sports.
                - allowsDogs (bool): If dogs are allowed.
                - restroom (bool): If restrooms are available.
                - reservations (bool): Whether reservations are accepted.
                - paymentOptions (Dict[str, bool]): Accepted payment methods.
                    - acceptsCashOnly (bool)
                    - acceptsCreditCards (bool)
                    - acceptsDebitCards (bool)
                    - acceptsNfc (bool)
                - accessibilityOptions (Dict[str, bool]): Accessibility features.
                    - wheelchairAccessibleEntrance (bool)
                    - wheelchairAccessibleRestroom (bool)
                    - wheelchairAccessibleParking (bool)
                    - wheelchairAccessibleSeating (bool)
                - googleMapsUri (str): URI to the place on Google Maps.
                - websiteUri (str): URI of the place’s website.
                - internationalPhoneNumber (str): International formatted phone number.
                - nationalPhoneNumber (str): National formatted phone number.
                - iconMaskBaseUri (str): Base URI of the place icon.
                - iconBackgroundColor (str): Background color of the place icon.
                - plusCode (Dict[str, str]): Plus code information.
                    - globalCode (str)
                    - compoundCode (str)
                - primaryTypeDisplayName (Dict[str, str]): Localized type display name.
                    - text (str)
                    - languageCode (str)
                                - photos (List[Dict[str, Any]]): List of photo metadata.
                    - name (str): Resource name of the photo.
                    - widthPx (int): Width of the photo in pixels.
                    - heightPx (int): Height of the photo in pixels.
                    - googleMapsUri (str): Link to the photo on Google Maps.
                    - flagContentUri (str): URI to flag inappropriate content.

                - postalAddress (Dict[str, Any]): Structured address data.
                    - addressLines (List[str]): Unstructured address lines.
                    - recipients (List[str]): Recipient names (e.g., business or person).
                    - sublocality (str): Sublocality (e.g., district or neighborhood).
                    - postalCode (str): Postal or ZIP code.
                    - organization (str): Business or organization name.
                    - revision (int): Revision number of the address format.
                    - locality (str): City or town.
                    - administrativeArea (str): State, province, or region.
                    - languageCode (str): Language of the address.
                    - regionCode (str): Country/region code.
                    - sortingCode (str): Sorting code for mail delivery.

                - reviewSummary (Dict[str, str]): Summary for reviews.
                    - flagContentUri (str): URI to flag review summary.

                - reviews (List[Dict[str, Any]]): List of user reviews.
                    - name (str): Identifier of the review.
                    - googleMapsUri (str): Link to the full review.
                    - flagContentUri (str): URI to flag the review.
                    - rating (float): Rating given by the reviewer.
                    - relativePublishTimeDescription (str): Human-readable time since published.
                    - publishTime (str): ISO timestamp of review publication.
                    - authorAttribution (Dict[str, str]): Reviewer information.
                        - displayName (str): Name of the reviewer.
                        - photoUri (str): Photo URI of the reviewer.
                        - uri (str): Link to reviewer's profile.

                - addressDescriptor (Dict[str, Any]): Contextual descriptors.
                    - areas (List[Dict[str, str]]): Named areas around the address.
                        - name (str): Area name.
                        - placeId (str): Unique identifier.
                        - containment (str): Relationship to the place (e.g., CONTAINED_IN).
                    - landmarks (List[Dict[str, Any]]): Points of interest near the address.
                        - placeId (str): Place ID of the landmark.
                        - name (str): Landmark name.
                        - spatialRelationship (str): Relative position to the main place.
                        - straightLineDistanceMeters (float): Distance in meters.
                        - travelDistanceMeters (float): Travel distance in meters.
                        - types (List[str]): Types associated with the landmark.

                - googleMapsLinks (Dict[str, str]): Collection of relevant Google Maps links.
                    - photosUri (str): URI for viewing photos.
                    - writeAReviewUri (str): Link to write a review.
                    - placeUri (str): Link to the place.
                    - reviewsUri (str): Link to all reviews.
                    - directionsUri (str): Link to directions.

                - evChargeOptions (Dict[str, Any]): EV charging information.
                    - connectorCount (int): Total number of connectors.
                    - connectorAggregation (List[Dict[str, Any]]): Aggregated connector stats.
                        - availabilityLastUpdateTime (str): Last update timestamp.
                        - availableCount (int): Number of available connectors.
                        - maxChargeRateKw (float): Maximum charging rate.
                        - outOfServiceCount (int): Number of out-of-service connectors.
                        - type (str): Connector type.
                        - count (int): Total count of this connector type.

                - parkingOptions (Dict[str, bool]): Parking availability.
                    - paidGarageParking (bool)
                    - valetParking (bool)
                    - paidParkingLot (bool)
                    - freeStreetParking (bool)
                    - freeGarageParking (bool)
                    - freeParkingLot (bool)
                    - paidStreetParking (bool)

                - generativeSummary (Dict[str, str]): AI-generated insights.
                    - overviewFlagContentUri (str): URI to flag the summary.

                - fuelOptions (Dict[str, Any]): Fuel price information.
                    - fuelPrices (List[Dict[str, str]]): Price data per fuel type.
                        - type (str): Type of fuel.
                        - updateTime (str): Timestamp of last update.

                - timeZone (Dict[str, str]): Time zone data.
                    - id (str): Time zone identifier.
                    - version (str): Time zone database version.

                - subDestinations (List[Dict[str, str]]): Locations within the place.
                    - name (str): Name of the sub-destination.
                    - id (str): Unique identifier.

                - containingPlaces (List[Dict[str, str]]): Larger areas containing this place.
                    - name (str): Name of the containing place.
                    - id (str): Place ID.

            - contextualContents (List[Dict[str, Any]]): Additional insights related to places.
                - justifications (List[Dict[str, Any]]): Justifications for showing the place.
                    - businessAvailabilityAttributesJustification (Dict[str, bool]):
                        - takeout (bool)
                        - delivery (bool)
                        - dineIn (bool)
                    - reviewJustification (Dict[str, Any]):
                        - highlightedText (Dict[str, Any]):
                            - text (str): Review excerpt.
                            - highlightedTextRanges (List[Dict[str, int]]):
                                - startIndex (int): Start index of highlight.
                                - endIndex (int): End index of highlight.

    Raises:
        ValueError: If 'textQuery' is missing.
    """
    filtered_places = []

    # Determine the maximum number of results (using pageSize if provided, else maxResultCount defaulting to 20)
    max_results = request.get("pageSize") or request.get("maxResultCount", 20)

    # Get text query; required.
    text_query = request.get("textQuery", "").lower()
    if not text_query:
        raise ValueError("textQuery is required.")

    # Optional filters:
    strict_type_filtering = request.get("strictTypeFiltering", False)
    included_type = request.get("includedType")
    price_levels = request.get("priceLevels", [])
    open_now = request.get("openNow", False)
    min_rating = request.get("minRating", None)
    include_pure = request.get("includePureServiceAreaBusinesses", True)

    # Location restriction: assume circle filtering if provided.
    location_restriction = request.get("locationRestriction", {})
    circle = location_restriction.get("circle", {})
    if circle:
        center = circle.get("center", {})
        radius = circle.get("radius", 0.0)
        center_lat = center.get("latitude")
        center_lon = center.get("longitude")
    else:
        center_lat = center_lon = radius = None

    # languageCode for potential localized text adjustment.
    language_code = request.get("languageCode")

    # Loop through our static DB and apply filters.
    for place in DB.values():
        # Filter by textQuery: check if the query appears in the place name or formattedAddress.
        name_field = place.get("name", "").lower()
        formatted_address = place.get("formattedAddress", "").lower()
        if text_query not in name_field and text_query not in formatted_address:
            continue

        # Filter by strict type filtering.
        if strict_type_filtering and included_type:
            if place.get("primaryType") != included_type:
                continue

        # Filter by priceLevels if provided.
        if price_levels:
            if place.get("priceLevel") not in price_levels:
                continue

        # Filter by openNow if required.
        if open_now:
            current_hours = place.get("currentOpeningHours", {})
            if not current_hours.get("openNow", False):
                continue

        # Filter by minRating if provided.
        if min_rating is not None:
            if place.get("rating", 0) < min_rating:
                continue

        # Filter out pure service area businesses if includePure is False.
        if not include_pure:
            if place.get("pureServiceAreaBusiness", False):
                continue

        # Filter by locationRestriction if provided.
        if center_lat is not None and center_lon is not None and radius is not None:
            place_location = place.get("location", {})
            place_lat = place_location.get("latitude")
            place_lon = place_location.get("longitude")
            if place_lat is None or place_lon is None:
                continue
            distance = _haversine_distance(center_lat, center_lon, place_lat, place_lon)
            if distance > radius:
                continue

        # Optionally adjust localized text if languageCode is provided.
        if language_code:
            display = place.get("displayName", {})
            if display.get("languageCode", "") != language_code:
                continue

        filtered_places.append(place)

        if len(filtered_places) >= max_results:
            break

    # Construct the response.
    response = {
        "routingSummaries": [],  # Routing summaries are not supported yet.
        "places": filtered_places,
        "contextualContents": [],  # Not implemented.
        "nextPageToken": "",  # Not implemented.
    }
    return response
