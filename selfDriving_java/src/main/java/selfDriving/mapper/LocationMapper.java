package selfDriving.mapper;

import org.apache.ibatis.annotations.Param;
//import selfDriving.domain.*;

public interface LocationMapper {
    void position(@Param("x")Double x, @Param("y")Double y, @Param("deviceType")String deviceType);
}
