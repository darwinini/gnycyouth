/**
 * Injects pickup selection UI into checkout via wp_footer
 * Single pickup selection applies to entire order.
 */

add_action( 'wp_enqueue_scripts', 'enqueue_pickup_checkout_scripts' );
function enqueue_pickup_checkout_scripts() {
    if ( ! is_checkout() ) {
        return;
    }

    wp_enqueue_script(
        'pickup-checkout',
        get_stylesheet_directory_uri() . '/js/pickup-checkout.js',
        [ 'jquery' ],
        '1.0.4',
        true
    );

    wp_localize_script( 'pickup-checkout', 'pickupData', [
        'ajaxUrl'   => admin_url( 'admin-ajax.php' ),
        'nonce'     => wp_create_nonce( 'pickup_nonce' ),
        'cartItems' => get_pickup_cart_items(),
    ]);
}

/**
 * Get cart items that have pickup configured.
 */
function get_pickup_cart_items() {
    $items = [];

    if ( ! WC()->cart ) {
        return $items;
    }

    foreach ( WC()->cart->get_cart() as $cart_key => $cart_item ) {
        $product_id = $cart_item['product_id'];
        $locations  = get_field( 'available_pickup_locations', $product_id );

        if ( empty( $locations ) ) {
            continue;
        }

        $location_options = [];
        foreach ( $locations as $location ) {
            $location_options[] = [
                'id'      => $location->ID,
                'name'    => $location->post_title,
                'address' => get_field( 'location_address', $location->ID ),
            ];
        }

        $variation_label = '';
        if ( ! empty( $cart_item['variation'] ) ) {
            $parts = [];
            foreach ( $cart_item['variation'] as $key => $value ) {
                $parts[] = ucfirst( str_replace( 'attribute_pa_', '', $key ) ) . ': ' . ucfirst( $value );
            }
            $variation_label = ' (' . implode( ', ', $parts ) . ')';
        }

        $items[] = [
            'cart_key'     => $cart_key,
            'product_id'   => $product_id,
            'variation_id' => $cart_item['variation_id'] ?? 0,
            'name'         => get_the_title( $product_id ) . $variation_label,
            'locations'    => $location_options,
        ];
    }

    return $items;
}

/**
 * Get the intersection of locations available across ALL pickup items in cart.
 */
function get_shared_pickup_locations() {
    $items = get_pickup_cart_items();

    if ( empty( $items ) ) {
        return [];
    }

    $shared_ids = array_column( $items[0]['locations'], 'id' );

    foreach ( $items as $item ) {
        $item_location_ids = array_column( $item['locations'], 'id' );
        $shared_ids        = array_intersect( $shared_ids, $item_location_ids );
    }

    if ( empty( $shared_ids ) ) {
        return [];
    }

    $locations = [];
    foreach ( $items[0]['locations'] as $location ) {
        if ( in_array( $location['id'], $shared_ids ) ) {
            $locations[] = $location;
        }
    }

    return $locations;
}

/**
 * Get combined pickup date range across all cart items.
 */
function get_combined_pickup_date_range() {
    $items      = get_pickup_cart_items();
    $start_date = null;
    $end_date   = null;

    foreach ( $items as $item ) {
        $product_id    = $item['product_id'];
        $product_start = get_field( 'pickup_start_date', $product_id );
        $product_end   = get_field( 'pickup_end_date', $product_id );

        if ( $product_start ) {
            $start_dt = DateTime::createFromFormat( 'Ymd', $product_start );
            if ( ! $start_date || $start_dt > $start_date ) {
                $start_date = $start_dt;
            }
        }

        if ( $product_end ) {
            $end_dt = DateTime::createFromFormat( 'Ymd', $product_end );
            if ( ! $end_date || $end_dt < $end_date ) {
                $end_date = $end_dt;
            }
        }
    }

    return [
        'start' => $start_date ? $start_date->format( 'Ymd' ) : null,
        'end'   => $end_date   ? $end_date->format( 'Ymd' )   : null,
    ];
}

/**
 * Inject pickup fields HTML into footer.
 */
add_action( 'wp_footer', 'render_pickup_fields_in_footer' );
function render_pickup_fields_in_footer() {
    if ( ! is_checkout() ) {
        return;
    }

    $items     = get_pickup_cart_items();
    $locations = get_shared_pickup_locations();

    if ( empty( $items ) || empty( $locations ) ) {
        return;
    }

    $product_names = array_unique( array_column( $items, 'name' ) );
    $date_range    = get_combined_pickup_date_range();
    ?>
    <div id="pickup-selection-wrapper" style="display:none;">
        <div id="pickup-selection-inner" style="
            margin: 20px 0;
            padding: 20px;
            border: 1px solid #e5e5e5;
            border-radius: 8px;
            box-sizing: border-box;
            width: 100%;
            overflow: hidden;
        ">
            <h3 style="margin-bottom: 10px;">Pickup Details</h3>

            <div class="pickup-item"
                 data-date-range-start="<?php echo esc_attr( $date_range['start'] ?? '' ); ?>"
                 data-date-range-end="<?php echo esc_attr( $date_range['end'] ?? '' ); ?>">

                <!-- Location -->
                <p class="form-row form-row-wide" style="box-sizing: border-box;">
                    <label>Pickup Location <span class="required">*</span></label>
                    <select class="pickup-location-select input-text"
                            name="pickup_location_order"
                            style="width:100%; padding: 8px; box-sizing: border-box; max-width: 100%;">
                        <option value="">— Select a location —</option>
                        <?php foreach ( $locations as $location ) : ?>
                        <option value="<?php echo esc_attr( $location['id'] ); ?>"
                                data-address="<?php echo esc_attr( $location['address'] ); ?>">
                            <?php echo esc_html( $location['name'] . ' — ' . $location['address'] ); ?>
                        </option>
                        <?php endforeach; ?>
                    </select>
                </p>

                <!-- Calendar -->
                <div id="pickup-calendar-wrapper" style="display:none; margin-top: 15px; box-sizing: border-box; width: 100%;">
                    <label style="font-weight: bold; display: block; margin-bottom: 10px;">
                        Pickup Date <span class="required">*</span>
                    </label>
                    <input type="hidden" name="pickup_date_order" id="pickup_date_order">
                    <div id="pickup-calendar" style="
                        background: #fff;
                        border: 1px solid #e5e5e5;
                        border-radius: 8px;
                        overflow: hidden;
                        width: 100%;
                        max-width: 100%;
                        box-sizing: border-box;
                        user-select: none;
                    ">
                        <!-- Header -->
                        <div id="pickup-cal-header" style="
                            background: #1a1a2e;
                            color: #fff;
                            display: flex;
                            align-items: center;
                            justify-content: space-between;
                            padding: 12px 16px;
                            box-sizing: border-box;
                        ">
                            <button type="button" id="pickup-cal-prev" style="
                                background: none; border: none; color: #fff;
                                font-size: 20px; cursor: pointer; padding: 0 8px; line-height: 1;
                            ">&#8249;</button>
                            <span id="pickup-cal-month-label" style="font-weight: bold; font-size: 15px;"></span>
                            <button type="button" id="pickup-cal-next" style="
                                background: none; border: none; color: #fff;
                                font-size: 20px; cursor: pointer; padding: 0 8px; line-height: 1;
                            ">&#8250;</button>
                        </div>

                        <!-- Day headers -->
                        <div id="pickup-cal-days-header" style="
                            display: grid;
                            grid-template-columns: repeat(7, 1fr);
                            background: #f4f4f4;
                            border-bottom: 1px solid #e5e5e5;
                            box-sizing: border-box;
                        "></div>

                        <!-- Grid -->
                        <div id="pickup-cal-grid" style="
                            display: grid;
                            grid-template-columns: repeat(7, 1fr);
                            gap: 4px;
                            padding: 8px;
                            box-sizing: border-box;
                        "></div>

                        <!-- Loading -->
                        <div id="pickup-cal-loading" style="
                            display: none; text-align: center;
                            padding: 20px; color: #999;
                        ">Loading available dates...</div>
                    </div>
                </div>

                <!-- Time Slots -->
                <div id="pickup-timeslots-wrapper" style="display:none; margin-top: 15px; box-sizing: border-box; width: 100%;">
                    <label style="font-weight: bold; display: block; margin-bottom: 10px;">
                        Pickup Time <span class="required">*</span>
                    </label>
                    <input type="hidden" name="pickup_time_order" id="pickup_time_order">
                    <div id="pickup-timeslots-grid" style="width: 100%; box-sizing: border-box;"></div>
                    <div id="pickup-timeslots-loading" style="
                        display: none; color: #999;
                        font-size: 13px; margin-top: 8px;
                    ">Loading time slots...</div>
                </div>

            </div>
        </div>
    </div>

    <script>
    jQuery(function($) {

        var availableDates  = [];
        var currentYear     = 0;
        var currentMonth    = 0;
        var selectedDate    = null;
        var selectedTime    = null;
        var currentLocation = null;

        var dayNamesDesktop = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
        var dayNamesMobile  = ['S','M','T','W','T','F','S'];
        var monthNames      = ['January','February','March','April','May','June',
                               'July','August','September','October','November','December'];

        function renderDayHeaders() {
            var $header  = $('#pickup-cal-days-header');
            var isMobile = window.innerWidth < 480;
            var names    = isMobile ? dayNamesMobile : dayNamesDesktop;
            $header.empty();
            names.forEach(function(name) {
                $header.append(
                    $('<div>').text(name).css({
                        'text-align'  : 'center',
                        'padding'     : '8px 4px',
                        'font-size'   : isMobile ? '11px' : '12px',
                        'font-weight' : 'bold',
                        'color'       : '#555',
                    })
                );
            });
        }

        function toYmd(date) {
            var y = date.getFullYear();
            var m = String(date.getMonth() + 1).padStart(2, '0');
            var d = String(date.getDate()).padStart(2, '0');
            return y + m + d;
        }

        function renderCalendar() {
            var $grid  = $('#pickup-cal-grid');
            var $label = $('#pickup-cal-month-label');
            $grid.empty();

            $label.text(monthNames[currentMonth] + ' ' + currentYear);

            var today    = new Date();
            var minYear  = today.getFullYear();
            var minMonth = today.getMonth();

            $('#pickup-cal-prev').css('opacity',
                ( currentYear === minYear && currentMonth === minMonth ) ? '0.3' : '1'
            );

            var firstDay    = new Date(currentYear, currentMonth, 1).getDay();
            var daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

            for (var i = 0; i < firstDay; i++) {
                $grid.append($('<div>'));
            }

            for (var d = 1; d <= daysInMonth; d++) {
                var date    = new Date(currentYear, currentMonth, d);
                var ymd     = toYmd(date);
                var isAvail = availableDates.indexOf(ymd) !== -1;
                var isSel   = ymd === selectedDate;

                var $cell = $('<div>').text(d).css({
                    'text-align'    : 'center',
                    'padding'       : '10px 4px',
                    'border-radius' : '6px',
                    'font-size'     : '14px',
                    'cursor'        : isAvail ? 'pointer' : 'default',
                    'font-weight'   : isAvail ? 'bold' : 'normal',
                    'background'    : isSel ? '#1a1a2e' : ( isAvail ? '#fff' : '#f0f0f0' ),
                    'color'         : isSel ? '#fff' : ( isAvail ? '#1a1a2e' : '#bbb' ),
                    'border'        : isAvail && ! isSel ? '1px solid #d0d0d0' : '1px solid transparent',
                    'transition'    : 'background 0.15s, color 0.15s',
                });

                if (isAvail) {
                    $cell.attr('data-date', ymd);
                    $cell.on('mouseenter', function() {
                        if ( $(this).attr('data-date') !== selectedDate ) {
                            $(this).css({ 'background': '#e8eaf0', 'color': '#1a1a2e' });
                        }
                    }).on('mouseleave', function() {
                        if ( $(this).attr('data-date') !== selectedDate ) {
                            $(this).css({ 'background': '#fff', 'color': '#1a1a2e' });
                        }
                    }).on('click', function() {
                        selectedDate = $(this).attr('data-date');
                        $('#pickup_date_order').val(selectedDate);
                        renderCalendar();
                        loadTimeSlots(selectedDate);
                    });
                }

                $grid.append($cell);
            }
        }

        function loadDates(locationId, dateStart, dateEnd) {
            currentLocation = locationId;
            availableDates  = [];
            selectedDate    = null;
            selectedTime    = null;

            $('#pickup_date_order').val('');
            $('#pickup_time_order').val('');
            $('#pickup-cal-loading').show();
            $('#pickup-cal-grid').hide();
            $('#pickup-cal-days-header').hide();
            $('#pickup-timeslots-wrapper').hide().find('#pickup-timeslots-grid').empty();

            $.post(pickupData.ajaxUrl, {
                action     : 'get_pickup_dates',
                nonce      : pickupData.nonce,
                location_id: locationId,
                date_start : dateStart || '',
                date_end   : dateEnd   || '',
            }, function(response) {
                $('#pickup-cal-loading').hide();
                $('#pickup-cal-grid').show();
                $('#pickup-cal-days-header').show();

                if ( response.success && response.data.dates.length ) {
                    availableDates = response.data.dates.map(function(d) { return d.value; });

                    var firstDate = availableDates[0];
                    currentYear   = parseInt(firstDate.substring(0, 4));
                    currentMonth  = parseInt(firstDate.substring(4, 6)) - 1;

                    selectedDate = availableDates[0];
                    $('#pickup_date_order').val(selectedDate);

                    renderDayHeaders();
                    renderCalendar();
                    loadTimeSlots(selectedDate);
                } else {
                    $('#pickup-cal-grid').html(
                        '<p style="padding:15px;color:#999;text-align:center;grid-column:span 7;">No available dates for this location.</p>'
                    );
                }
            });
        }

        function loadTimeSlots(date) {
            selectedTime = null;
            $('#pickup_time_order').val('');

            var $wrapper = $('#pickup-timeslots-wrapper');
            var $grid    = $('#pickup-timeslots-grid');
            var $loading = $('#pickup-timeslots-loading');

            $grid.empty();
            $loading.show();
            $wrapper.slideDown(200);

            $.post(pickupData.ajaxUrl, {
                action     : 'get_pickup_slots',
                nonce      : pickupData.nonce,
                location_id: currentLocation,
                date       : date,
            }, function(response) {
                $loading.hide();

                if ( response.success && response.data.slots.length ) {

                    var $select = $('<select>')
                        .attr('id', 'pickup-timeslot-select')
                        .css({
                            'width'         : '100%',
                            'padding'       : '10px',
                            'font-size'     : '15px',
                            'border'        : '1px solid #d0d0d0',
                            'border-radius' : '6px',
                            'box-sizing'    : 'border-box',
                            'background'    : '#fff',
                            'color'         : '#1a1a2e',
                        });

                    $select.append($('<option>').val('').text('— Select a time —'));

                    response.data.slots.forEach(function(slot) {
                        var spotsMatch = slot.label.match(/\((\d+) spots? left\)/);
                        var spots      = spotsMatch ? parseInt(spotsMatch[1]) : 5;
                        var isLow      = spots <= 2;
                        var label      = isLow ? '⚠ ' + slot.label : slot.label;

                        $select.append(
                            $('<option>').val(slot.value).text(label)
                        );
                    });

                    $select.on('change', function() {
                        selectedTime = $(this).val();
                        $('#pickup_time_order').val(selectedTime);
                    });

                    $grid.append($select);

                } else {
                    $grid.html('<p style="color:#999;font-size:13px;">No time slots available for this date.</p>');
                }
            });
        }

        // Month navigation
        $('#pickup-cal-prev').on('click', function() {
            var today = new Date();
            if ( currentYear === today.getFullYear() && currentMonth === today.getMonth() ) {
                return;
            }
            currentMonth--;
            if (currentMonth < 0) { currentMonth = 11; currentYear--; }
            renderCalendar();
        });

        $('#pickup-cal-next').on('click', function() {
            currentMonth++;
            if (currentMonth > 11) { currentMonth = 0; currentYear++; }
            renderCalendar();
        });

        // Location change
        $(document).on('change', '.pickup-location-select', function() {
            var $item      = $(this).closest('.pickup-item');
            var locationId = $(this).val();
            var dateStart  = $item.data('date-range-start') || '';
            var dateEnd    = $item.data('date-range-end') || '';

            if ( ! locationId ) {
                $('#pickup-calendar-wrapper').slideUp(200);
                $('#pickup-timeslots-wrapper').slideUp(200);
                return;
            }

            $('#pickup-calendar-wrapper').slideDown(200);
            loadDates(locationId, dateStart, dateEnd);
        });

        // Re-render day headers on resize
        $(window).on('resize', function() {
            if (availableDates.length) {
                renderDayHeaders();
            }
        });

        // Show/hide entire pickup section
        function isLocalPickupSelected() {
            var $radio = $('input[name="shipping_method[0]"]:checked');
            if ( $radio.length ) return $radio.val().indexOf('local_pickup') !== -1;
            var $hidden = $('input[name="shipping_method[0]"][type="hidden"]');
            if ( $hidden.length ) return $hidden.val().indexOf('local_pickup') !== -1;
            return false;
        }

        function injectAndShow() {
            var $inner = $('#pickup-selection-inner');

            if ( ! $inner.parent().is('#payment') && $('#payment').length ) {
                $inner.insertBefore('#payment');
            }

            if ( isLocalPickupSelected() ) {
                $inner.show();

                // Auto-select if only one location
                $('.pickup-location-select').each(function() {
                    var $select  = $(this);
                    var $options = $select.find('option[value!=""]');
                    if ( $options.length === 1 && $select.val() === '' ) {
                        $select.val( $options.first().val() ).trigger('change');
                    }
                });
            } else {
                $inner.hide();
            }
        }

        setTimeout( injectAndShow, 500 );
        $( document.body ).on( 'updated_checkout', function() { setTimeout( injectAndShow, 300 ); });
        $( document.body ).on( 'change', 'input[name="shipping_method[0]"]', injectAndShow );

    });
    </script>
    <?php
}