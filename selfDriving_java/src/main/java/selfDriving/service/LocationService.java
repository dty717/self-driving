package selfDriving.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import selfDriving.mapper.LocationMapper;

@Service
public class LocationService {
 
    @Autowired
    LocationMapper locationMapper;
    
    @Transactional
    public void position(Double x, Double y, String deviceType) {
         locationMapper.position(x, y, deviceType);
    }
    
}
