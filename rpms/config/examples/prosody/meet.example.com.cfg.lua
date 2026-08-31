-- /etc/prosody/conf.avail/meet.example.com.cfg.lua
-- Замените meet.example.com и auth.meet.example.com на ваш FQDN.

plugin_paths = { "/usr/share/jitsi-meet/prosody-plugins/" }

VirtualHost "meet.example.com"
    authentication = "internal_hashed"
    ssl = {
        key = "/etc/prosody/certs/meet.example.com.key";
        certificate = "/etc/prosody/certs/meet.example.com.crt";
    }
    modules_enabled = {
        "bosh";
        "websocket";
        "smacks";
        "speakerstats";
        "conference_duration";
        "muc_lobby_rooms";
        "muc_meeting_id";
        -- "reservations";      -- см. config-examples/reservation/
        -- "short_lived_token"; -- см. config-examples/file-sharing/
    }

Component "conference.meet.example.com" "muc"
    storage = "memory"
    modules_enabled = {
        "muc_meeting_id";
        "muc_domain_mapper";
        "muc_password_whitelist";
    }
    admins = { "focus@auth.meet.example.com" }
    muc_room_cache_size = 1000

VirtualHost "auth.meet.example.com"
    authentication = "internal_hashed"
    ssl = {
        key = "/etc/prosody/certs/auth.meet.example.com.key";
        certificate = "/etc/prosody/certs/auth.meet.example.com.crt";
    }

Component "focus.meet.example.com" "client_proxy"
    target_address = "focus@auth.meet.example.com"

Component "jitsi-videobridge.meet.example.com"
    component_secret = "JVB_COMPONENT_SECRET"
